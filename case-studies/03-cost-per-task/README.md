# Case Study 3: Cutting cost without cutting quality

> Status: TEMPLATE. Replace the bracketed parts with your own work and delete this line.

## Learning goal
Apply the free levers (caching, batch, output limits) before trading away quality.

## The product problem
[A workload with a large repeated prompt, e.g. a 6K-token policy doc plus a short user question.]

## Levers to test, in order
1. **Prompt caching**: stable prefix first, volatile content last. Verify `cache_read_input_tokens > 0`.
2. **Batch API**: for anything non-urgent (50% cheaper).
3. **`max_tokens` and structured output**: stop paying for rambling.
4. **Effort step-down**: only with an eval to prove quality holds.
5. **Model tier step-down**: last.

## Results
| Configuration | Quality | $/task | Change vs baseline |
|---|---|---|---|
| Baseline | | | |
| + caching | | | |
| + batch | | | |
| + effort step-down | | | |

## Business case
[Monthly savings at your assumed volume, and the quality risk accepted.]
