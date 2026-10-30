# E100 (Arham): phrase reuse against controls matched in vocabulary richness

- **Pre-registration:** `E100_PREREG.md` (sha256 3e54483c…), commit 36307ca.
- **Script:** `experiments/e100_matched_phrases.py` (sha256 caca99f1…).
- **Results:** `experiments/results/e100.json`, log `e100_run.log`. Run 2026-10-30, 325 s.

## Verdict (pre-registered rule): BETWEEN. E099's M × 1/3 is withdrawn (net M × 3)

## Why this test
E099 scored M × 1/3 because the Voynich's Q3 (repeated 3-word sequences ÷ the number a shuffle gives) was above every
copy-generator stretch. But a richer vocabulary makes chance repeats rarer and so raises Q3, and no E099 control was as
rich as the Voynich (6,077 word types in 28,841 tokens). E100 compares the Voynich only with texts of the same
richness (± 15%: 5,165–6,989 types).

## Results
| Group (richness-matched) | n | Q3 | Raw repeated 3-word tokens | Repeated 4-word tokens |
|---|---|---|---|---|
| Meaningful (L*: 10 Bibles: Czech, Oromo, Byzantine Greek, Hungarian, Chichewa, Polish, Slovak, Serbian, Uyghur, Ukrainian) | 10 | min 13.6, p10 16.9, median 43 | 1,270–4,527 | 223–1,634 |
| Copy generator (G*: 4 settings) | 15 | 0.67–6.54 | 0–97 | 0–4 |
| **Voynich** | | **10.8** (236 vs 20.9 by shuffle; sd 3.1) | **236** | **0** |

VALID: L* p10 16.9 > G* max 6.54, with 10 and 15 members. The Voynich lies between the two groups: 4.3 above the
generator maximum and 2.8 below the lowest matched language. No boundary was within 0.5 sd, so no seed check was
needed. By the pre-registered table, BETWEEN withdraws E099's factor.

## Unscored observations
- **Richness alone can inflate Q3 for meaningless text.** The generator with no glyph-sequence check (`canFollow none`,
  8,350–10,030 types, outside the band) gives Q3 7.5–33.8, which is in the language range. E099's ratio was therefore
  not a safe yardstick on its own.
- **Raw counts:** Voynich 236 repeated triples is 2.4× the highest matched generator stretch (97) and 5.4× below the
  lowest matched language (1,270). It reuses more 3-word sequences than this copying, and far fewer than languages.
- **No 4-word repeats:** Voynich 0, matched languages ≥ 223, matched generator 0–4. On longer phrases the Voynich sits
  with the generator.
- The matched generator stretches that use random source choice reach the band only by losing most copying
  (raw repeats 0–16). The page-local settings in the band (`err10_position`, one `err10_reuse0_pos0`) give 33–97.

## Ledger
E099's M × 1/3 is withdrawn, so the ledger returns to its post-E098 values: **M 0.4897, L 0.3594, C 0.0676, O 0.0833**.
