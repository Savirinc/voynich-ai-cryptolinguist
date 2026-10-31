# E105 (Arham, Reddit idea R11): vowel harmony with o, a, y as vowels

- **Pre-registration:** `E105_PREREG.md` (sha256 a3658938…), commit 87ddcef.
- **Script:** `experiments/e105_vowel_harmony.py`.
- **Results:** `experiments/results/e105.json`, log `e105_run.log`. Run 2026-10-31.

## Verdict (pre-registered): NO HARMONY, no factor
EXCESS is the information one vowel gives about the next vowel in the same word, beyond what vowel positions give.

| Group | EXCESS (bits) |
|---|---|
| Harmony languages: Turkish, Azerbaijani, Hungarian | +0.925, +0.839, +0.516 |
| 22 non-harmony languages | +0.000 (Romanian) to +0.154 (German); median about +0.09 |
| 60 copy-generator stretches | +0.000 to +0.020 |
| **Voynich (o, a, y)** | **−0.001** (permutation sd 0.0015) |

VALID (0.516 > 0.154). Once their positions in the word are accounted for, Voynich *o*, *a* and *y* do not depend on
one another at all. That is lower than every non-harmony language and at the bottom of the generator range.

**Unscored:** with *e* added as a fourth vowel, EXCESS is +0.031, like Latin (+0.031) or Swedish (+0.033), and far from
harmony.

## What it means
The Reddit vowel-harmony idea is rejected. Vowel choice in a Voynich word is fixed by the slot it sits in, not by
the other vowels in the word. No factor, because most real languages lack harmony too.

## Ledger
No change: M 0.7422, L 0.1816, C 0.0342, O 0.0421.
