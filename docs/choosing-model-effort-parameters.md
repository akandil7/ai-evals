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
- Defaults differ by model (Opus 5.5 and Haiku 5.5 default to `medium`; Sonnet 5.5 defaults to `high`). **Set it explicitly.**
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

## 7. Cheat sheet by workload

| Workload | Start with |
|---|---|
| Ticket triage or classification at scale | Haiku 5.5, `low`, structured output, batch where possible |
| Summarizing meetings or docs | Sonnet 5.5, `low` or `medium` |
| PRD or analysis drafting | Opus 5.5, `medium` or `high` |
| Agentic coding or research | Opus 5.5 or Sonnet 5.5, `high` or `xhigh`, task budget |
| Hard multi-hour agent runs | Fable 5.1, `xhigh` |

These are starting hypotheses. Your eval decides.
