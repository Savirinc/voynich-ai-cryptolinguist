# E110 (Arham): are p and f two forms of one letter, or different (possibly opposite) letters?

- **Pre-registration:** `E110_PREREG.md`, commit 01f01c7.
- **Script:** `experiments/e110_pf_same_or_different.py`.
- **Results:** `experiments/results/e110.json`, log `e110_run.log`.
- **Pair list:** `reports/data/pf_pairs.csv`.

## Verdict (pre-registered): SAME-LETTER-LIKE, no factor
The test asks whether the choice between *p* and *f* depends on which word it is, beyond scribe, paragraph position
and slot in the word. The answer is no: G 179.6, p 0.47. The 484 testable tokens in 83 word pairs behave as if every
word draws from the same *p*:*f* odds set by context. The verdict is not near a boundary, so no seed check was needed.

| Known answer | Caught as word-specific (p < 0.01) |
|---|---|
| Latin real letter pair (*s/t*) | 20/20 |
| Italian real letter pair (*r/l*; the prereg said *s/t*, see note) | 17/20 |
| Latin planted second pen form of *t* | 0/20 |
| Italian planted second pen form of *t* | 0/20 |
| **Voynich *p/f*** | **p 0.47: not word-specific** |

VALID. *Note:* the prereg said the rule picked *s/t* in both languages, which was true of the smoke-run cut. On the
locked run's cut, the same rule picked *r/l* for Italian. The rule is unchanged; only the prereg's description of its
outcome was wrong.

## Unscored
- **Every common pair leans the same way, towards *p*.**

  | Pair | *p* : *f* (after setting aside witnesses) |
  |---|---|
  | *opchedy/ofchedy* | 39 : 3 |
  | *opchey/ofchey* | 24 : 2 |
  | *pchedy/fchedy* | 30 : 7 |
  | *qopchedy/qofchedy* | 23 : 8 |
  | *opar/ofar* | 11 : 6 |
  | *cphy/cfhy* | 8 : 5 |
  | *p/f* written alone | 6 : 9 (the only one leaning to *f*) |

- **Shared pages:** of 79 pages with the *f*-version of a word, 15 also have its *p*-version. No permutation baseline
  was computed for this, although the script's docstring announced one, so it stays descriptive.

## What it means
At the level of words, *p* and *f* behave like **two forms of one letter**, not two letters with different meanings.
Which one a scribe wrote depends on who was writing and where (paragraph first lines, scribe 3's strong preference for
*p*), not on the word.

This fits the f57v finding. One letter can have two forms, and the form can still be used to mark something, such as
the two halves of the circle (X109) or opposite sides of other rings (E109, weak). It works like capital and small
letters, or the long and short *s* of old printing. "Opposite meanings" is not supported at word level; "same letter,
form chosen by position or context" is.

## Ledger
No change: M 0.7422, L 0.1816, C 0.0342, O 0.0421.
