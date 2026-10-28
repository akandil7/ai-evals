## First Run

### What I did  
I used a Kaggle dataset, limited to 50 test. Used 3 different model, using effort low and medium and a very low max_token. 

### Goal
The goal was to understand how to setup the environment, prepare/write the project and test things out.

### Lesson learned 
1. I should have tested with more tokens then keep reducing it till I achieve the desired result.
2. Check that runs finished before trusting scores. Opus medium scored 26% only because 31 replies were cut off by max_tokens. Raise the limit and rerun.
3. Higher effort uses more tokens. Reasoning counts against the same limit as the answer, so set max_tokens for the highest effort tested.
4. Flat accuracy across models points at the eval. Cheap and expensive models all scored about 50%, so the prompt, labels or grader may be the problem. Read some failed cases by hand.
5. About 50 cases is too few. One case is 2 points, so 48% vs 52% is noise. Add more cases.
6. Cost didn’t buy accuracy. Haiku is far cheaper with similar results. Start there once the eval is fixed.

### Next steps
1. Raise max_tokens and rerun.
2. Review failures to check the grader.
3. Add more test cases.
4. Compare again against the bar.


## Second Run

### What I did  
I updated kaggle dataset after reviewing test cases, i will re-run as changing multiple parameter would misslead the conclusion and see if any of the model is performing better.

### The results
![alt text](<runs-differences.png>)
![alt text](<models-bar.png>)

### Lessons learned
1. Every config is under $0.002, so cost only matters for choosing between passing configs, where Haiku and Sonnet are far cheaper than Opus.
2. Opus low misses on latency alone, by 0.7 s. Its p95 was 1.8 s in run 1 and 5.7 s now with nothing changed, so I suspect a slow tail or API load rather than a real change. Rerun a few times before ruling it out. It would still cost about 2x Sonnet for the same accuracy, so it’s unlikely to be worth it.
3. Opus medium’s failure isn’t a real result. The 30 cutoffs make its 36% meaningless, and its cost of $0.00178 is only $0.00022 under the limit, so a higher max_tokens could push it over.
4. Haiku is 4–6 points short on accuracy. It’s about 30x cheaper than Sonnet, so check whether the gap is real. Fix its cutoffs, then try prompt improvements.
5. Sonnet’s margin is thin. 66% vs the 60% bar is about 3 cases if you have around 50. With that sample size, the true accuracy could plausibly be below 60%.

### Next steps
1. Raise max_tokens and rerun everything, so no row has cutoff warnings.
2. Rerun Opus low 2–3 times to see whether its latency is consistently above 5 s.
3. Add cases and a blind hold-out set to check that Sonnet’s 66% holds, since the margin over 60% is small and the labels were edited after seeing failures.
4. Pick Sonnet low as the default candidate. It passes every limit, and it’s the same accuracy and cost as medium with the least thinking.
5. Try a Haiku prompt improvement only if the cost savings matter enough to chase, since it needs about 5 more points

## Last run 

### What I did  
I removed opus from the comparison as Haiku and sonnet were meeting the bar, now i want to test out what happens if no runs were cut off due to low max_tokens. Since the truncated/skipped were a small number, i only increased tokens to be 10x the number that was set and it worked well.

## Outcome
1. Haiku improved and now passes, probably because cutoffs are gone. It sits exactly on the 60% bar, so one case could flip it. Sonnet is stable at 64–66%.
2. Haiku is about 20x cheaper and slightly faster, for 4–6 points less accuracy (2–3 cases on 50). Latency is roughly equal.

### Recommendation 
Sonnet at low effort.
Low and medium are about the same (64% vs 66%, within noise) at the same cost, so low is simpler with less cutoff risk.
The extra cost is small: about $0.61 more per 1,000 cases.
Haiku’s zero margin means it might really be below the bar.
Choose Haiku low instead for very high volume (about $30 vs $640 per million cases), but only after confirming on more cases and a hold-out set that it holds at 60% or better.