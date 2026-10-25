# Choosing the Right Model, Effort, and Parameters

A PM's working guide. Prices and behaviors reflect the Claude API as of October 2026. Re-verify before shipping, because this changes often.

## 1. The decision order

Work top-down. Each step is cheaper to change than the one after it.

1. **Prompt and context quality**: fix this first; no model rescues a vague task.
2. **Caching and input hygiene**: free savings with no quality tradeoff.
3. **Effort level**: the main quality/cost/latency dial within one model.
4. **Model tier**: change only if measured results justify it.
5. **Multi-model cascades**: last resort, because caches are per-model.

## 2. Model tiers (cached pricing, per 1M tokens, input / output)

| Tier | Model ID | Price | Reach for it when |
|---|---|---|---|
| Fable 5.1 | `claude-fable-5-1` | $10 / $50 | Hardest reasoning, long-horizon agentic work |
| Opus 5.5 | `claude-opus-5-5` | $4 / $20 | Default for complex work: coding, analysis, agents |
| Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10 | Everyday coding, enterprise workflows, good speed/quality |
| Haiku 5.5 | `claude-haiku-5-5` | $0.10 / $0.50 | High-volume classification, extraction, routing, sub-agents |

PM heuristic: pick the **cheapest tier that passes your eval**, then raise effort before raising tier.

## 3. Effort

`output_config: {effort: "low" | "medium" | "high" | "xhigh" | "max"}`

- Controls thinking depth and total token spend. It is not just "quality".
- Starting points: `low` for chat, classification and sub-agents; `medium` for routine agentic work; `high` for intelligence-sensitive tasks; `xhigh` for hard coding and long-horizon agents; `max` only when measurement shows headroom.
- A newer model at lower effort often matches an older model at high effort. Test that before paying for a bigger tier.

## 4. Thinking

- Use adaptive thinking: `thinking: {type: "adaptive"}`. The model decides when and how much to think.
- The old `budget_tokens` setting is removed on current models and returns a 400. Effort replaces it.
- Thinking display is `omitted` by default. If you stream reasoning to users, set `display: "summarized"`, or users see a long pause before output.
- You are billed for thinking whatever the display setting.

## 5. Other dynamic parameters

| Parameter | What it does | PM note |
|---|---|---|
| `max_tokens` | Hard cap on output | Too low truncates mid-answer. Use about 16K non-streaming and about 64K streaming for open-ended work; use about 256 for classification. |
| Streaming | Tokens arrive as generated | Needed for long outputs and for UX. |
| Prompt caching | Reuses a stable prompt prefix | Biggest free cost lever. Verify with `usage.cache_read_input_tokens`. |
| Structured outputs | `output_config.format` constrains the response to a schema | Use instead of "please return JSON". |
| `tool_choice` | Controls tool use | Forced tool use is rejected on newer models; use `auto` plus a prompt instruction or `strict: true`. |
| Task budgets (beta) | Token ceiling for an agent loop | Advisory pacing, unlike `max_tokens`. |
| Fast mode (beta) | Same model, up to 2.5x output speed, premium price | Latency-critical paths only. |
| Batch API | Async at 50% cost | Anything not user-facing and not urgent. |

**Sampling parameters (`temperature`, `top_p`, `top_k`) are gone.** Newer models reject non-default values, and from 2026-10-21 any request that sends them returns a 400 on every model. Control variety and determinism through prompt and output-format design.

## 6. How to decide: the three metrics

Never choose on a vibe. For each candidate configuration measure:

1. **Quality**: pass rate on a fixed eval set of 20 to 50 real tasks.
2. **Cost per completed task**, not per request. A cheap request that needs three retries is not cheap.
3. **Latency**: p50 and p95 time to a usable answer.

Plot quality against cost per task. The efficient frontier is your answer, and the case studies in this repo are exactly that exercise.

## 7. Setting the pass bar

The bar is what turns "here are some numbers" into a yes or no answer. Without it, every run ends in an argument about whether 87% is good. Set it **before** you run any model. If you set it after seeing results, you will choose the bar that makes your preferred model pass.

### How to think about each number

Each threshold starts from a business question, not a model question.

**`min_accuracy`: what does a wrong answer cost?**

1. **Cost of an error.** If a misrouted ticket is re-queued by an agent in 30 seconds, errors are cheap and 85–90% may be enough. If a wrong label sends a refund request to a team that never answers it, or misses a security report, errors are expensive and you need 97% or more, or a human review step.
2. **Baseline.** Measure what happens today. If two human triagers agree on only 88% of tickets, labels above roughly 90% stop meaning much, because the "expected" answers are themselves noisy. The bar should match or modestly beat the current process, not chase 100%.
3. **Asymmetric errors.** Overall accuracy hides which mistakes happen. If one category is critical (for example `account_access`, where a customer is locked out), consider a separate per-label recall check rather than raising the overall bar.

**`max_cost_per_case_usd`: what can the business pay at volume?**

1. Start from a monthly budget and volume: `max_cost = monthly budget ÷ monthly volume`. Triage example: $200/month ÷ 100k tickets = $0.002.
2. Sanity-check it against what a human costs per item. If an agent spends 20 seconds triaging at $30/hour, that is about $0.17 per ticket, so the model is about 85 times cheaper even at the bar.
3. Estimate cost per model before running: `cost = input_tokens × input_price + output_tokens × output_price` (prices per 1M tokens in `configs/default.json`). For a triage ticket of roughly 120 input tokens and up to about 200 output tokens including thinking:

| Model | Approx. $/ticket | vs. $0.002 bar |
|---|---|---|
| Haiku 5.5 | ~$0.0001 | Far under |
| Sonnet 5.5 | ~$0.002 | Borderline; depends on how much it thinks |
| Opus 5.5 | ~$0.005 | Over |

So this bar is not neutral. It effectively says "Opus is too expensive for triage unless it answers very tersely." That is a deliberate product decision, and it should be stated as one. Replace these estimates with the real token counts from `results/*.csv` after the first run.

**`max_p95_latency_s`: who is waiting?**

1. **Is someone waiting live?** In a chat reply the user is watching, 2–3 seconds feels slow. In a background queue nobody watches, 30 seconds is fine.
2. **Use p95, not the average.** The average hides the slow tail. p95 means 1 in 20 requests is slower than this, which is what users actually notice.
3. **Effort affects latency.** Higher effort means more thinking tokens, so more time. A latency bar often decides the effort level more than the model does.

Triage example: tickets are routed before a human picks them up, so nobody waits on the label live. 5 seconds keeps the queue close to real time. If a customer-facing auto-reply depends on the label, tighten it to about 2 seconds.

### Make sure your case count can support the bar

A bar is only as precise as the number of cases behind it. With *n* cases, one mistake moves accuracy by 1/*n*, and the uncertainty is wide:

| Result | Observed accuracy | 95% confidence range (Wilson) |
|---|---|---|
| 11 / 12 | 0.92 | 0.65 – 0.99 |
| 45 / 50 | 0.90 | 0.79 – 0.96 |
| 90 / 100 | 0.90 | 0.83 – 0.94 |
| 180 / 200 | 0.90 | 0.85 – 0.93 |

With 12 cases, a model scoring 11/12 "passes" a 0.90 bar but could plausibly be a 70% model. Rules of thumb:

- Use at least 50 cases before trusting a 0.90 bar, and 100–200 for a bar of 0.95 or higher.
- Run each case several times per configuration and average, because a single run can be lucky.
- When two models are within a few points of each other, treat them as tied and let cost or latency decide.

### A worked process

1. Write down the three business questions above and answer them in one line each. Those lines become `bar_rationale`.
2. Turn the answers into numbers and put them in `bar`.
3. Write the cases and expected answers, with enough cases to support the accuracy bar.
4. Run the eval. Read the results, but **do not move the bar to make a favorite model pass**. If the bar turns out to be wrong, change it because of new information about the business (volume, error cost, baseline), and note why in `bar_rationale`.
5. Pick the cheapest configuration that meets the bar. If none do, go back up the decision order in section 1 (prompt first), not straight to a bigger model.

## 8. Cheat sheet by workload

| Workload | Start with |
|---|---|
| Ticket triage or classification at scale | Haiku 5.5, `low`, structured output, batch where possible |
| Summarizing meetings or docs | Sonnet 5.5, `low` or `medium` |
| PRD or analysis drafting | Opus 5.5, `medium` or `high` |
| Agentic coding or research | Opus 5.5 or Sonnet 5.5, `high` or `xhigh`, task budget |
| Hard multi-hour agent runs | Fable 5.1, `xhigh` |

These are starting hypotheses. Your eval decides.
