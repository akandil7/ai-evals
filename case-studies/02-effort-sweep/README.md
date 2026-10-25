# Case Study 2: How much thinking is worth paying for?

> Status: TEMPLATE. Replace the bracketed parts with your own work and delete this line.

## Learning goal
Treat effort (`low` to `max`) as a product dial with a measurable cost/quality curve.

## The product problem
[Pick a task where reasoning depth plausibly matters, e.g. "draft a prioritization recommendation from 5 conflicting stakeholder inputs".]

## Method
1. Put 15 to 30 tasks in `tasks.jsonl` (one JSON object per line: `id`, `prompt`, optional `expected`).
2. Run `python experiments/effort_sweep.py case-studies/02-effort-sweep/tasks.jsonl`.
3. Grade answers (rubric or a second model as judge, spot-checked by you).
4. Chart quality vs cost per task for each model x effort cell.

## Hypotheses (write before running)
- H1: [e.g. Sonnet 5.5 at `medium` matches Opus 5.5 at `low` for this task]
- H2: [e.g. `xhigh` gives no measurable gain over `high`]

## Results
[Embed chart. State which hypotheses held.]

## Decision
[Chosen model + effort, expected monthly cost at [N] requests/day, and the quality you are accepting.]

## Learnings
[What surprised you? Where did more effort NOT help?]
