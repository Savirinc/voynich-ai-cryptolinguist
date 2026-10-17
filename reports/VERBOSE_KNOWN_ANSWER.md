# E016: known-answer cracking test for the E014 cipher class

Pre-registered: reports/E016_PREREG.md (sha256 d890d133…). Script: experiments/e016_verbose_known_answer.py.
Results: experiments/results/e016.json, e016_run.log. 46 attacks, 4 restarts x 600k SA iterations each, 1.5 h.

## Pre-registered verdicts
| Decision | Result | Verdict |
|---|---|---|
| Crack with true-language LM (>= 80% letters) | 3 of 8 full-size tasks | **NOT CRACKABLE** |
| Language picked by lowest gap | 4 of 8 | **NOT IDENTIFIED** |
| Confidence threshold (lowest control gap) | 0.200 (rugg seed 1); 0 of 3 successes below it | **NO USABLE THRESHOLD** |
| Quarter size (10k letters), reported only | 2 of 8 | — |

Step 3 (attack Voynich DEV) therefore does **not** go ahead.

## What the numbers say
- **When the attack works, it really works.** The three Italian cracks read 93.5% correct letters, e.g. decoded
  `anchedasoliaquattroccusavanodeltuconfidenzialeinpresenzadeiterzi…` vs truth
  `anchedasoliaquattrocchiusavanodeltuconfidenzialeinpresenzadeiterzi…`. Two quarter-size Italian texts (10k
  letters) also cracked (92–93%), consistent with the Shannon estimate that ~600–800 letters suffice in principle.
- **Success is a rare search event, not a matter of text length.** Every success came from exactly one restart
  landing in the right basin (per-char score ≈ −2.18 to −2.24) while the other three stalled at ≈ −2.5 to −2.6.
  Latin never landed in 3 keys x 4 restarts at full size, nor in 3 quarter-size tasks. The bottleneck is the search.
- **Gap is not a safe success signal.** Failed runs sit at gap 0.59–0.71, successes at 0.24–0.30, but one
  meaningless rugg control reached 0.200, below every success. The rugg controls left 53–61% of words unparsed
  (real-cipher texts: ~4.7%), so they are scored on far fewer, more repetitive components (18.7k components, 123
  symbols for seed 1), which flatters the LM score. Language identification failed because, for failed runs, the
  German LM gives the lowest gap regardless of plaintext.
- Letter-shuffled Latin controls behaved as expected (gap 0.73–0.74, accuracy 8%).

## Implications (not pre-registered; for the next pre-registration)
1. Search: many more restarts and/or better initialisation (e.g. start from the best partial keys, word-level
   moves, merged-word splitting), measured by restart success rate on these same known-answer tasks.
2. Confidence: gap alone is unusable. Candidates to test against controls: inventory parse rate (Voynich DEV
   20.2% unparsed vs rugg 53–61% vs cipher 4.7%), agreement between independent restarts on the key, and a gap
   compared against controls matched on component count and parse rate.
3. The test still assumes Greshko's published inventory; a different Voynich inventory is not covered.
