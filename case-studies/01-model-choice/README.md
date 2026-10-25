# Case Study 1: Which model should power this feature?

> Status: TEMPLATE. Replace the bracketed parts with your own work and delete this line.

## Learning goal
Choose a model tier from evidence, not brand or habit.

## The product problem
[Pick a real or realistic feature, e.g. "auto-triage inbound support tickets into 6 categories". Describe the user, the job to be done, and what a wrong answer costs.]

## Success criteria (write these BEFORE testing)
- Quality bar: [e.g. >= 92% category accuracy on 40 labeled tickets]
- Cost ceiling: [e.g. < $0.002 per ticket]
- Latency ceiling: [e.g. p95 < 3s]

## Method
1. Build an eval set of 20 to 50 realistic, **synthetic or anonymized** examples with known answers. Never use real customer data.
2. Run Haiku 5.5, Sonnet 5.5 and Opus 5.5 at the same effort.
3. Record quality, cost per task and latency (see `experiments/effort_sweep.py`).

## Results
| Model | Quality | $/task | p95 latency |
|---|---|---|---|
| Haiku 5.5 | | | |
| Sonnet 5.5 | | | |
| Opus 5.5 | | | |

## Decision and rationale
[Which model, and why. Name the runner-up and what would change your mind.]

## What I'd do next
[Risks, monitoring, when to re-evaluate when a new model ships.]
