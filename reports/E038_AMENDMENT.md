# E038 amendment (before the rerun): a bug fix, with no change to the method or rules

Written 2026-10-22. The original pre-registration (`E038_PREREG.md`, sha 89c4cc56…25a4) and script stay locked and
unchanged. The rerun uses `experiments/e038_sign_inventory_v2.py`.

## What went wrong
The first run hung on the alternation d±, at the pair *aiin/daiin*.
- The "two unrelated words" baseline (RAND) needs a word about as common as *daiin* (662). The only one is *ol*.
- When the first random word was *or* or *al*, which are one glyph from *ol*, the code retried forever.

The run was stopped after 2 h 21 min.

## The fix (v2), and nothing else
1. When no word has a similar count, the fallback list of the 20 nearest-count words now also respects the
   exclusion list. Before, it could return the pair's own words.
2. The search for the second unrelated word gives up after 50 tries. It then takes the nearest-count word that is
   not one glyph from the first.

Same seed, same controls, same measures, same thresholds and verdict rules.

## What had already been seen (disclosed)
The first run printed the controls and the first three alternations before hanging:
- FREE control S_page 1.12, S_nbr 1.03;
- CONTRAST control S_page 0.51, S_nbr 0.58 (neither measure VOID);
- e/ee: FREE VARIANT (t_page 0.80, t_nbr 1.09);
- r/l: MIXED (t_page 0.37, t_nbr −0.46);
- t/k: MIXED (t_page 0.61, t_nbr 1.17).

The fix can change the random draws, so the v2 numbers may differ slightly. **The v2 results are the ones that
count.** If any of the first three verdicts changes, both versions will be reported.
