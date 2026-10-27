# E072: is ot/ok a detachable front piece? DETACHABLE, GENERATOR TOO (no factor)

Run 2026-10-27 under `E072_PREREG.md` (locked; commit 651cabd). Script `experiments/e072_front_pieces.py`; results
`experiments/results/e072.json`, log `e072_run.log`. Runtime 10 s.

## In one paragraph
Taking *ot* or *ok* off a Voynich word leaves a word of its own more often than taking two signs off a matched ordinary
word (0.61 vs 0.48, z +3.66, 10/10 seeds). So *ot/ok* is detachable, like Arabic *al-* or Hungarian *meg-*. But the
copy generator, which knows no language, does the same thing more strongly (0.88–0.94, z +4.7 to +5.4), so this does
not separate a language from a meaningless process. No ledger factor, as pre-registered.

## Validation
| Text | Front piece | targets | REM | matched control | z (median, 10 seeds) |
|---|---|---|---|---|---|
| Arabic (consonants) | ال | 398 | 0.405 | 0.112 | +19.44 |
| Hebrew (consonants) | ה | 353 | 0.524 | 0.385 | +5.47 |
| Hungarian | meg | 130 | 0.369 | 0.035 | +21.58 |
| Indonesian | ber | 98 | 0.398 | 0.052 | +15.97 |
| the four texts and Voynich | pseudo-targets | 98–398 | | | −1.04 to +1.64 (all within) |
| Voynich layer 1 (internal) | q on qo-words | 253 | 0.723 | 0.457 | +9.01 |

10/10 checks pass: VALID.

## Voynich and generator
| Set | targets | REM | control | z | seeds > 3 |
|---|---|---|---|---|---|
| **layer 2: ot/ok (primary)** | 186 | 0.613 | 0.483 | **+3.66** (3.50–3.79) | 10/10 |
| ot/ok, label words only | 85 | 0.647 | 0.486 | +3.12 | 10/10 |
| layer 3: qot/qok | 152 | 0.625 | 0.611 | +0.37 | 0/10 |
| op/of | 35 | 0.971 | 0.517 | +5.63 | 10/10 |
| o alone, on o + tall-letter words | 223 | 0.565 | 0.504 | +1.94 | 0/10 |
| generator seed 31, ot/ok | 53 | 0.943 | 0.598 | +5.29 | 10/10 |
| generator seed 32 | 59 | 0.881 | 0.583 | +4.67 | 10/10 |
| generator seed 33 | 72 | 0.875 | 0.563 | +5.44 | 10/10 |

**Verdict: DETACHABLE, GENERATOR TOO.** Factor none.

## What the detail shows (descriptive)
- The remainder is a word when it starts with a sign that can start a word: *okaiin→aiin*, *okal/otal→al*,
  *okar/otar→ar*, *oty/oky→y*, *okol/otol→ol*. It is never a word when it starts with *e*: *otedy/okedy→edy*,
  *okeol→eol*, *okey→ey* (0 to 4 occurrences each). Voynich words do not begin with *e*. So detachability follows the
  sign-order rules of the script, which the generator copies, rather than anything specific to *ot/ok*.
- *ot* and *ok* take the same remainders: 65 shared of 89 and 97, consistent with *t ≈ k* (E038).
- *q* is the most detachable layer (z +9), as E038 and E059 showed. *o* alone is not (z +1.9), as on 2026-10-25.
  *qot/qok* together are not, beyond their controls (z +0.4): their matched controls are already very word-like.

## For the label-class programme
Arham's question was whether *ot/ok* is root-like (fused) or marker-like (detachable). The text says marker-like, but
in a way a copying process also produces, so it cannot yet be read as language evidence. For the title + name reading
(E073 candidate, zodiac images) this fixes what to compare: *ot* and *ok* behave as one front piece, and the part after
it (*al*, *ar*, *aiin*, *ol*, *y*) is mostly an ordinary common word.
