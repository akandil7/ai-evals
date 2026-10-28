"""Run one eval folder across the models x efforts in a config; grade, and print a summary.

Usage:
    pip install anthropic
    python runner.py evals/triage                       # uses configs/default.json
    python runner.py evals/triage --config configs/default.json --limit 5

Auth comes from your environment (never put keys in this repo). Every run spends real API money,
so start with --limit.

An eval folder holds:
    task.json    name, instructions, labels, grader, bar
    cases.jsonl  one {"id", "input", "expected"} per line
"""
import argparse
import csv
import json
import math
import statistics
import time
from datetime import datetime
from pathlib import Path

import anthropic


def exact_match(answer, case, task):
    """Pass if the model's reply, normalized, equals the expected label."""
    return answer.strip().lower() == case["expected"].strip().lower()


# LLM-as-judge goes here later: a grader(answer, case, task) -> bool that asks a model to
# score the answer against a rubric. Register it in GRADERS and set "grader" in task.json.
GRADERS = {"exact_match": exact_match}


def ask(client, model, effort, task, case, max_tokens):
    labels = ", ".join(task["labels"])
    start = time.time()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        system=task["instructions"],
        messages=[{"role": "user", "content": f"Labels: {labels}\n\nTicket:\n{case['input']}"}],
    )
    latency = time.time() - start
    text = "".join(b.text for b in resp.content if b.type == "text")
    return text, resp.usage.input_tokens, resp.usage.output_tokens, latency, resp.stop_reason


def p95(values):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("eval_dir")
    parser.add_argument("--config", default="configs/default.json")
    parser.add_argument("--limit", type=int, default=None, help="only run the first N cases")
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir)
    task = json.loads((eval_dir / "task.json").read_text())
    config = json.loads(Path(args.config).read_text())
    cases = [json.loads(l) for l in (eval_dir / "cases.jsonl").read_text().splitlines() if l.strip()]
    if args.limit:
        cases = cases[: args.limit]
    grade = GRADERS[task["grader"]]

    client = anthropic.Anthropic()
    Path("results").mkdir(exist_ok=True)
    out_path = Path("results") / f"{task['name']}-{Path(args.config).stem}-{datetime.now():%Y%m%d-%H%M%S}.csv"
    summary = {}
    total = len(config["models"]) * len(config["efforts"]) * len(cases)
    done = 0
    print(f"{task['name']}: {total} calls, max_tokens={config['max_tokens']}, writing {out_path}")

    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case", "model", "effort", "expected", "answer", "passed",
                         "in_tokens", "out_tokens", "latency_s", "cost_usd", "stop_reason"])
        for model, price in config["models"].items():
            for effort in config["efforts"]:
                rows = []
                for case in cases:
                    answer, tin, tout, lat, stop = ask(client, model, effort, task, case, config["max_tokens"])
                    cost = (tin * price["input_per_mtok"] + tout * price["output_per_mtok"]) / 1e6
                    ok = grade(answer, case, task)
                    rows.append((ok, lat, cost, stop))
                    writer.writerow([case["id"], model, effort, case["expected"], answer.strip(),
                                     ok, tin, tout, round(lat, 2), round(cost, 6), stop])
                    f.flush()  # keep partial results if the run dies midway
                    done += 1
                    print(f"[{done}/{total}] {model} {effort} {case['id']}: "
                          f"{'pass' if ok else 'FAIL'} ({answer.strip()[:30]!r}) {tout} tok {lat:.1f}s {stop}")
                summary[(model, effort)] = rows

    bar = task.get("bar", {})
    print(f"\n{task['name']}: {len(cases)} cases   (details: {out_path})\n")
    print(f"{'model':<20}{'effort':<8}{'accuracy':>9}{'$/case':>10}{'p95 s':>8}  meets bar?")
    for (model, effort), rows in summary.items():
        acc = sum(r[0] for r in rows) / len(rows)
        cost = statistics.mean(r[2] for r in rows)
        lat = p95([r[1] for r in rows])
        meets = (acc >= bar.get("min_accuracy", 0)
                 and cost <= bar.get("max_cost_per_case_usd", float("inf"))
                 and lat <= bar.get("max_p95_latency_s", float("inf")))
        print(f"{model:<20}{effort:<8}{acc:>9.0%}{cost:>10.5f}{lat:>8.1f}  {'yes' if meets else 'no'}")
        cut = sum(r[3] == "max_tokens" for r in rows)
        if cut:
            print(f"{'':<28}warning: {cut} replies cut off by max_tokens")


if __name__ == "__main__":
    main()
