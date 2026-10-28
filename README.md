# ai-evals

To objectively answer 'which model and effort level is good enough?' for any given task, I built a lightweight evaluation harness that measures quality, cost, and latency. Since cost is what matter most today, along with accuracy, AI evals is important to learn & apply. To keep things practical and cost-effective, the harness restricts scope to 3 core Claude models (excluding Fable) and 2 lower effort settings (low and medium, omitting high, extra, and max), isolating how reduced reasoning depth impacts performance. Running a test case only once per configuration can lead to flaky data. Multi-run averages (or pass@k rates) are essential to ensure a model didn't just get lucky on a single run.

### Evaluation Gaps
1. Task Taxonomy: Group test cases by task type (e.g., summarization vs. structured extraction). A model that excels at one can completely fail at another.
2. Prompt-Variant Comparison: Test multiple phrasing styles per task. Evaluating a single prompt measures how well a model likes your specific wording, not its true capability, leading to brittle real-world results.

### Lesson learned
Check docs section for lesson learned, will add the TL;DR here once all is clear.

## Get Started 

### Project Layout
```
evals/<task>/task.json     what is tested: instructions, labels, grader, pass bar
evals/<task>/cases.jsonl   test cases: id, input, expected answer
configs/default.json       models, effort levels, prices
runner.py                  runs an eval across models x efforts and prints a summary
results/                   CSV outputs of each run (git-ignored)
docs/                      notes, starting with how to choose model, effort and parameters
```

### Run
**CRITICAL:** Credentials come from your environment. Never commit keys. Each run costs real money.

```bash
pip install anthropic
python runner.py evals/triage --limit 3    # cheap smoke test first
python runner.py evals/triage
```

### Add a new eval
1. Copy `evals/triage` to `evals/<new-task>`.
2. Edit `task.json`: instructions, labels and the bar (min accuracy, max cost per case, max p95 latency). Explain each number in `bar_rationale`; see [Setting the pass bar](docs/choosing-model-effort-parameters.md#7-setting-the-pass-bar).
3. Write your cases in `cases.jsonl`. Write the expected answers yourself, **before** running any model.
4. Run it.

## Roadmap
1. Exact-match grading on classification tasks (done).
2. LLM-as-judge for open-ended outputs: add a grader function in `runner.py`'s `GRADERS` that scores an answer against a rubric, and spot-check its verdicts against your own.

## Rules
- Synthetic or anonymized data only: no customer or employer-confidential content.
- Model names and prices change. Re-check `configs/default.json`.

