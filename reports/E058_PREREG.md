# E058 pre-registration (E057 v2): word-specific self-repetition, with enough words to have power

Written 2026-10-24, before the run. Script: `experiments/e058_word_repeat_individuality_v2.py`. Updates
`reports/LEDGER.md`.

## Same question as E057
Do individual words differ in how often they stand right next to themselves, beyond what their form (family)
predicts? A real vocabulary gives words individual behaviour; a family-level generator does not (`FORUM_SYNTHESIS.md`).

## What changed from E057 (which was VOID for lack of eligible words)
1. **Eligible words:** every word seen **at least 10 times** (E057 required at least 1 *expected* same-line repeat,
   which left 26 Voynich words).
2. **Statistic:** a likelihood-ratio deviance. G measures how badly "one repeat rate per family" fits the words'
   observed back-to-back counts, with expected counts E_w from the exact within-line formula and O_w ~ Poisson(rate ×
   E_w).
   - **Null:** a parametric bootstrap under the family model (2,000 draws, rates refitted).
   - **Output:** z and a one-sided p.

**Unchanged from E057:** texts, sample size (28,841 tokens), family definition (first unit, last two characters,
families with at least 2 words), the generator stretches and the decision rule. Words watched and reported: dal,
shey, saiin, okaiin, daiin, chol, qokeedy, qokeey, chedy, shedy, dy, ol, aiin.

## Decision
| Outcome | Rule | Factor |
|---|---|---|
| VOID | fewer than 3 of the 5 reference languages have z above every generator sample **and** p < 0.01 | none |
| WORD-SPECIFIC (vocabulary-like) | Voynich z > every generator sample **and** p < 0.01 | M × 1/3 |
| FAMILY-LEVEL (generator-like) | Voynich z ≤ the generator median | M × 3 |
| INCONCLUSIVE | otherwise | none |

## Disclosed
- **E057's numbers are known:** Voynich z +0.4 on 26 words; Indonesian z +5.1 on 13 words; generator −1.7 to +0.9.
  E058 is a redesign after a VOID, not a second try after a negative result. It is the last attempt in this family:
  no v3 unless a new fact calls for it.
- **No E058 statistic has been computed.**
