"""Run one task set across models x effort levels and record quality inputs, cost and latency.

Usage:
    pip install anthropic
    python experiments/effort_sweep.py case-studies/02-effort-sweep/tasks.jsonl

Auth: the SDK reads credentials from your environment or `ant auth login`.
Never paste keys into this file. Running this spends real API money, so keep tasks.jsonl small.
Each line of tasks.jsonl: {"id": "t1", "prompt": "...", "expected": "optional ground-truth note"}
"""
import csv
import json
import sys
import time

import anthropic

# $ per 1M tokens (input, output). Cached pricing, re-check before relying on it.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}
EFFORTS = ["low", "medium", "high"]


def run(client, model, effort, prompt):
    start = time.time()
    resp = client.messages.create(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
    )
    latency = time.time() - start
    text = "".join(b.text for b in resp.content if b.type == "text")
    in_price, out_price = PRICES[model]
    cost = (resp.usage.input_tokens * in_price + resp.usage.output_tokens * out_price) / 1_000_000
    return text, resp.usage.input_tokens, resp.usage.output_tokens, latency, cost


def main(path):
    client = anthropic.Anthropic()
    tasks = [json.loads(line) for line in open(path) if line.strip()]
    with open("experiments/results.csv", "w", newline="") as f:
        out = csv.writer(f)
        out.writerow(["task", "model", "effort", "in_tokens", "out_tokens", "latency_s", "cost_usd", "answer"])
        for t in tasks:
            for model in PRICES:
                for effort in EFFORTS:
                    text, i, o, lat, cost = run(client, model, effort, t["prompt"])
                    out.writerow([t["id"], model, effort, i, o, round(lat, 2), round(cost, 6), text])
                    print(t["id"], model, effort, f"${cost:.4f}", f"{lat:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1])
