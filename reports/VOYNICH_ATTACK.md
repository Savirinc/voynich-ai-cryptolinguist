# E018 (step 3): the validated E017 attack on Voynich — NO CLAIM

Pre-registered: reports/E018_PREREG.md (sha256 1a27ca8d…). Script: experiments/e018_voynich_attack.py.
Results: experiments/results/e018.json, e018_run.log. LOCKED_TEST leaves excluded (15).

## Result
| Text | Words | Unparsed | LM | Agreement | Long-word coverage | Claim |
|---|---|---|---|---|---|---|
| DEV | 28,841 | 5,821 (20.2%) | la / it / fr / de | 0.568 / 0.508 / 0.654 / 0.686 | 0.005 / 0.002 / 0.002 / 0.006 | none |
| Currier A | 8,806 | 2,142 (24.3%) | la / it / fr / de | 0.522 / 0.656 / 0.579 / 0.737 | 0.007 / 0.003 / 0.001 / 0.009 | none |
| Currier B | 19,490 | 3,505 (18.0%) | la / it / fr / de | 0.591 / 0.499 / 0.544 / 0.619 | 0.005 / 0.002 / 0.003 / 0.005 | none |

**Verdict: NO CLAIM.** Every Voynich attack looks like the E017 meaningless controls (agreement 0.50–0.74 vs
controls' max 0.83 and real cracks' min 0.99; long-word coverage ≤ 0.009 vs controls' max 0.028 and cracks' min
0.139). Not borderline.

## Interpretation (as pre-registered)
Voynich is not the E014 cipher class with the published Naibbe inventory and Latin, Italian, French or German
plaintext, as far as an attack validated to crack that class (8/8, no false claims) can detect.

Not excluded: a different glyph inventory (the 20% unparsed rate, against ~5% for true Naibbe ciphertext, already
says the published tables do not fit Voynich's words exactly), other plaintext languages, abbreviated plaintext,
or other mechanisms. The LOCKED_TEST pages were not used.
