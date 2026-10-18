# E017: known-answer test, second attempt — PASSED

Pre-registered: reports/E017_PREREG.md (sha256 b7315b56…). Script: experiments/e017_portfolio_known_answer.py.
Results: experiments/results/e017.json, e017_run.log. 72 attacks, 128 restarts x 100k iterations each, ~2.5 h.

## Pre-registered verdicts
| Decision | Result | Verdict |
|---|---|---|
| Crack (true-LM accuracy >= 80%) | 8 of 8 full-size texts (92.3–93.7%) | **CRACKABLE** |
| No false claims | 0 of 32 control attacks, 0 wrong-language decodes | **SAFE** |
| Language identified | 8 of 8 (the true language was the only claim every time) | **IDENTIFIED** |
| Quarter size (10k letters), reported only | 8 of 8 cracked (88.6–92.1%), 7 of 8 claimed | — |

**Step 3: GO.**

## Margins
| | Agreement | Long-word coverage (7+ letters) |
|---|---|---|
| Controls and wrong-language decodes, maximum | 0.829 | 0.028 |
| Successful cracks, minimum | 0.991 | 0.139 |
| Claim threshold | 0.95 | 0.08 |

The one unclaimed quarter-size success (Latin key 2: 88.6% accurate, agreement 0.917) fell below the agreement
bar: the rule errs towards silence, as intended.

## What changed from E016
Delta scoring (≈10x faster) let the budget go to 128 short restarts instead of 4 long ones. Latin went from 0/3
to 3/3. The LM gap was replaced as the success signal by two independent checks (restart agreement, long-word
coverage), and every control was attacked with all four LMs.

## Limits
Same plaintext stretches as E016 and the development runs (fresh keys). Assumes Greshko's inventory and the four
languages; plaintext that is heavily abbreviated would lower long-word coverage.
