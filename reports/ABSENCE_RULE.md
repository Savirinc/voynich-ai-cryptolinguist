# Ledger amendment: how "searched, not found" lowers a hypothesis (absence accounting)

Written 2026-10-24. Locked, with its sha256 in the commit. It amends `reports/LEDGER.md`, section 5 (update rules),
from now on.

## Why
Until now, only a scored test could move the ledger. Validated searches that came back empty (E049, E050) moved
nothing, because no part of L had been assigned to the forms they searched. That is not proper Bayes: "searched with
a working method and not found" is evidence ("the dog that did not bark").

## The rule
1. **Split each hypothesis into the forms it can take**, each with a prior share (below). Shares are set *before*
   any further search. Their ranges are stated.
2. **A search is VALIDATED** if a pre-registered known-answer test showed it finds that form (E047-style), with no
   false claims.
3. **When a validated search of a form returns NO CLAIM,** that form's share is multiplied by its **miss rate** m, and
   the hypothesis is multiplied by (1 − s·(1 − m)), where s is the form's share of the hypothesis. All hypotheses are
   then renormalised.
4. **Default miss rate m = 0.2,** even when known-answer power was 100%. It leaves room for mismatches the known-answer
   test could not cover (e.g. Biblical LMs against a herbal text). A search needs a separate pre-registered argument
   to use a smaller m.
5. **The same rule applies to M and C.** For example, a validated test that "this kind of gibberish generator cannot
   produce X" lowers that M-form the same way.

## Forms of L (shares of L; set now)
| Form | Share | Range |
|---|---|---|
| L-alpha-known: an attested language with surviving texts, written letter by letter (alphabet or abjad, homophones allowed) in the invented script | 0.35 | 0.20–0.50 |
| L-syll: a known language written with syllable signs | 0.20 | 0.10–0.30 |
| L-abbrev: abbreviation- or notation-heavy writing of a known language | 0.15 | 0.05–0.25 |
| L-unattested: a lost, unrecorded or constructed language | 0.20 | 0.10–0.35 |
| L-other / mixed | 0.10 | 0.05–0.20 |

**Within L-alpha-known, by language:**
| Language | Share |
|---|---|
| Hebrew | 0.15 |
| Turkish | 0.05 |
| Latin | 0.15 |
| Slavic shortlist (Czech 0.08, Serbian-Croatian 0.05, Slovak 0.03, Ukrainian 0.04) | 0.20 |
| Romanian | 0.03 |
| Italian | 0.15 |
| Other European and unlisted | 0.27 |

**Forms of C:** homophonic or simple letter substitution of Hebrew, Turkish or Latin is 0.10 of C. The rest is other
ciphers.

## Disclosure
These shares are written **after** E049–E050, whose result was NO CLAIM. To limit hindsight, the shares follow the
E042 shortlist order and general plausibility. A sensitivity check is reported with every application.

## First application: E049 + E050 (Hebrew, Turkish, Latin; VOY23 class; validated by E047)
- **L:** s = 0.35 × (0.15 + 0.05 + 0.15) = 0.1225, so L × (1 − 0.1225 × 0.8) = **× 0.902**.
- **C:** s = 0.10, so C × (1 − 0.10 × 0.8) = **× 0.92**.
- **Result:** M 0.006 → **0.0066**, L 0.970 → **0.9688**, C 0.023 → **0.0234**, O 0.001 → **0.0011**.
- **Sensitivity:** with m = 0.1 and s = 0.2, L is 0.9685.

## Why the number barely moves (stated plainly)
When L holds 97%, removing a 12% slice of it leaves L still far ahead, because the alternatives are tiny to begin
with. **The real question is whether M deserves to be as low as 0.006.**
- M was pushed down mainly by E030–E032: real languages *can* double words, and *one* generator failed.
- Since then, C21 (E043–E046) and E048 have shown habits that non-meaningful writing approaches and meaningful prose
  does not. These were never scored.

That asymmetry is the next thing to fix: M must face, and be able to win, tests as strong as those L has faced.
