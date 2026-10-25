# ai-evals

A small, reusable harness for testing which Claude model and effort level is good enough for a task, measured on quality, cost and latency.

## Layout
```
evals/<task>/task.json     what is tested: instructions, labels, grader, pass bar
evals/<task>/cases.jsonl   test cases: id, input, expected answer
configs/default.json       models, effort levels, prices
runner.py                  runs an eval across models x efforts and prints a summary
results/                   CSV outputs of each run (git-ignored)
docs/                      notes, starting with how to choose model, effort and parameters
```

## Run
```bash
pip install anthropic
python runner.py evals/triage --limit 3    # cheap smoke test first
python runner.py evals/triage
```
Credentials come from your environment. Never commit keys. Each run costs real money.

## Add a new eval
1. Copy `evals/triage` to `evals/<new-task>`.
2. Edit `task.json`: instructions, labels and the bar (min accuracy, max cost per case, max p95 latency).
3. Write your cases in `cases.jsonl`. Write the expected answers yourself, **before** running any model.
4. Run it.

## Roadmap
1. Exact-match grading on classification tasks (done).
2. LLM-as-judge for open-ended outputs: add a grader function in `runner.py`'s `GRADERS` that scores an answer against a rubric, and spot-check its verdicts against your own.
3. Prompt-variant comparison and batch runs.

## Rules
- Synthetic or anonymized data only: no customer or employer-confidential content.
- Model names and prices change. Re-check `configs/default.json`.
