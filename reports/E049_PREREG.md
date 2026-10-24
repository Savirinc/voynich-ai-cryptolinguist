# E049 pre-registration (attack step 3b): the validated attack on Voynich itself

Written 2026-10-24, before the run. Script: `experiments/e049_attack_voynich.py`. LOCKED_TEST leaves are not used.

## What runs
- **Attack:** E047's attack, unchanged (it passed: 9/9 cracks, 0 false claims). Same LMs (Hebrew, Turkish and Latin,
  from Genesis to 2 Kings), same search (32 restarts × 30,000 steps), same scoring.
- **Primary target: Voynich Currier A,** DEV prose, cleaned (e-runs → e, t → k), cut into S3 units. The 23 commonest
  A signs are the cipher symbols; rarer units (about 1%) are dropped, and the count is reported. Word spaces are kept.
  A is the size E047 validated (about 8,800 words).
- **Secondary target: Currier B,** the same treatment at its full size. This is reported only, since the method was
  not validated at that size or on B's rigidity.
- **Controls in the same run:** 2 sign-shuffled copies of Voynich A and 2 fresh copy-generator samples, each against
  all three LMs.

## Claim rule (fixed now; stricter than E047)
CLAIM requires all of:
- agreement ≥ 0.95;
- lexrate ≥ 0.514 (E047's DEV threshold);
- lexrate ≥ (the highest control lexrate in this run) + 0.10.

The extra 0.10 margin is added because the generator came within 0.09 of the threshold in E047.

## Decision
| Outcome | Rule | Next |
|---|---|---|
| VOID | any control reaches agreement ≥ 0.95 and lexrate ≥ 0.514 | no conclusion |
| **CLAIM** | Voynich A is claimed under exactly **one** language | **E050:** the frozen key is applied once to the LOCKED_TEST leaves. Only a confirmed reading earns a ledger factor (L × 30), to be pre-registered in E050. |
| AMBIGUOUS | claims under more than one language | treated as no claim |
| **NO CLAIM** | otherwise | Recorded as *searched, not found*: Voynich A is not Hebrew, Turkish or Latin written letter by letter in a 23-sign script (with homophones, about 12% spelling slips and intact word order). The search had power 9/9 on known answers. This is empirical, not a logical exclusion, so no ledger factor. |

## Limits (stated now)
- **The LMs are Biblical.** A herbal or medical text in one of these languages would share less vocabulary with
  them, so its lexrate could fall below the bar even if the language is right. A NO CLAIM therefore does not exclude
  a *practical* text in these languages as strongly as a sacred one.
- **Classes not covered:** syllabic signs; abbreviation; vowel-less writing of Turkish or Latin; nulls; languages
  other than these three.
- **Decoded samples are printed for transparency.** Short decoded strings that happen to look like words are expected
  even from gibberish (E047: generator lexrate up to 0.42), and are **not evidence**.

## What was seen before writing this (disclosed)
- E047's results, and Voynich A's sign inventory.
- Nothing from an attack on Voynich.
