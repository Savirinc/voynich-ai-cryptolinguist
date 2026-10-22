# E038 (attack step 1b): the true sign inventory — results

Pre-registration `reports/E038_PREREG.md` (sha 89c4cc56…25a4). Amendment before the rerun:
`reports/E038_AMENDMENT.md`, a bug fix to an endless loop with nothing else changed. Script
`experiments/e038_sign_inventory_v2.py`. Results: `experiments/results/e038.json`, `e038_run.log`. This is a
measurement under working assumption L; no ledger change.

**The first-run verdicts were unchanged by the fix:** e/ee FREE VARIANT, r/l MIXED, t/k MIXED.

## Controls
| Control | S_page | S_nbr |
|---|---|---|
| FREE (Latin, e written E at random) | 1.09 | 1.03 |
| CONTRAST (Latin r/l, t/s, e/i minimal pairs) | 0.48 | 0.58 |

Separation is 0.60 and 0.45, both ≥ 0.4, so **Part A is valid**.

## Part A: the five alternations
t = 1 means "like one word, written two ways"; t = 0 means "like two different Latin words".

| Alternation | Pairs | t_page (same pages?) | t_nbr (same neighbours?) | Verdict (rule) | Plain reading |
|---|---|---|---|---|---|
| **e / ee** | 85 | 0.92 | 1.12 | **FREE VARIANT** | **One sign.** *e* and *ee* are written interchangeably. |
| **t / k** | 127 | 0.70 | 1.13 | MIXED | Almost one sign. Neighbours are the same; pages just miss the 0.75 bar, so some sections prefer one form. |
| **q ±** | 86 | 0.54 | 0.87 | MIXED | Same neighbours, partly different pages. **q looks like a spelling habit tied to section, not a word-changing prefix.** |
| **d ±** | 161 | 0.05 | 0.54 | MIXED | **Strongly different pages.** Forms with and without d (*chey/chedy*, *shey/shedy*, *aiin/daiin*) live in different parts of the book. |
| **r / l** | 107 | 0.41 | −0.48 | MIXED | **Different neighbours**, even more different than real Latin minimal pairs. r and l are not interchangeable: they mark something grammatical (e.g. *-ol* vs *-or* in different sentence slots). |

**What MIXED means here:** no row except e/ee meets a pre-registered bar. The plain readings follow the direction of
the two measures, and they are descriptive, not verdicts.

## Part B: positional forms (Arabic/Urdu-style) — VOID
The control failed. Latin with word-final *s* written *S* scored only at the 35th percentile on context similarity
(needed: 90th).
- **Why:** in a real language, the letters before a final *s* (*-us, -is, -as*) differ from those before an inner
  *s*. So "same letter, different position" doesn't show up as "same left context".
- **So:** this method cannot detect positional forms, and the question stays **open**. The one Voynich pair it
  flagged (*i/m*) is not reported as a finding.

## Part C: q
| | Words starting with q: first word of line | other words |
|---|---|---|
| Currier A | 14.6% | 9.7% |
| Currier B | 13.1% | 18.7% |

- q-words are about twice as common inside B lines as inside A lines.
- Together with the Part A row (same neighbours, partly different pages), **q behaves like a spelling or section
  habit, not like a meaning prefix** such as "not" or "opposite". A prefix that changed meaning would change a word's
  neighbours, and q does not.
- This is not a verdict: the rule said MIXED.

## What this means for the sign inventory
| Sign question | Status |
|---|---|
| e and ee | **Merge** (one sign) |
| t and k | Probably merge (near the bar). Test again on the merged inventory. |
| q- | Spelling or section habit; keep, but don't treat it as a meaning-carrier |
| d | Tied to section or scribe. Check against Currier A/B and Davis's five scribes. |
| r and l | **Keep separate.** They carry a grammatical difference. |
| Positional forms | Untested; this method can't see them |

**The biggest new lead is d.** Its forms split across the book far more than any other alternation, which is
exactly what a difference between scribes or dialects would look like.
