# E100 pre-registration: phrase reuse with richness-matched controls (Arham, 2026-10-30)

## Question
E099 found Voynich Q3 = 11.9 (repeated 3-word sequences ÷ shuffle expectation), above every copy-generator stretch
(max 4.75), and scored M × 1/3. But Q rises with vocabulary richness, and no E099 control was as rich as the Voynich
(6,077 word types in 28,841 tokens; generator about 3,800). **Does the Voynich still reuse phrases beyond meaningless
copying when the controls have the same vocabulary richness?**

## Data
- Voynich: DEV clean prose tokens, poured into DEV line lengths (as E099; LOCKED_TEST leaves excluded).
- Meaningful: E099's 69 texts (61 eBible translations + Pliny, abbreviated Pliny, Avicenna, Quran, Mahabharata, Lojban
  Alice, Culpeper, Latin farming prose), each cut to 28,841 tokens with seed 100100.
- Meaningless: the Timm & Schinner copy generator on a declared grid of **10 settings × 5 fresh seeds (11–15) = 50
  stretches**, with no other variants (rule 9):
  default; error_rate 10; error_rate 10 + reuse_last 0 + same_position 0; error_rate 10 + sourceChooser position;
  sourceChooser random + add_remove 40 + combine_split 40; error_rate 2 + random; random; error_rate 5 + random;
  canFollow none; canFollow none + error_rate 10.

## Procedure
Script `experiments/e100_matched_phrases.py`, which reuses E099 v2's `measure` unchanged: within-line phrasal 3-grams,
RP3, 20 whole-text shuffles, Q3 = (RP3 + 1) / (shuffle mean + 1).
- Richness = distinct word types in the 28,841-token stretch. Matched band = Voynich types ± 15% (5,165–6,989).
- L* = meaningful texts in the band; G* = generator stretches in the band.
- Validity: |G*| ≥ 10, |L*| ≥ 8, and L* Q3 10th percentile > G* Q3 maximum.

## Decision table (E100 supersedes E099's scoring of the same question)
| Outcome | Rule | E099+E100 factor on M | Net change to the current ledger |
|---|---|---|---|
| PHRASES LIKE LANGUAGE | Voynich Q3 ≥ L* p10 and > G* max | × 1/3 (E099 kept, fragile flag removed) | none |
| NO PHRASES (GENERATOR-LIKE) | Voynich Q3 ≤ G* max and < L* min | × 3 (E099's opposite outcome) | M × 9 |
| BETWEEN | otherwise | × 1 (E099 withdrawn) | M × 3 |
| VOID | validity fails | × 1 (E099 withdrawn: the statistic does not separate language from copying at Voynich richness) | M × 3 |

Rule 8: if Voynich Q3 is within 0.5 shuffle-sd of a boundary, 10 fresh shuffle seeds must give the same verdict
(≥ 8 of 10), otherwise BETWEEN. Unscored: raw RP3 and RP4 against L* and G*; Q3 against richness for all texts.

## Seen beforehand
- All of E099 (Voynich Q3 11.9, RP3 236, shuffle 18.9; meaningful min 3.63, p10 6.50, median 19.6; generator 2.0–4.75;
  Voynich RP4 = 0).
- Word-type counts (not Q) of all 69 meaningful texts on a first-28,841-token cut: in the band were gax, grcbyz, nya,
  hrv, ukr1871, hun, slk, latVUC, azb, uigara (10).
- Word-type counts (not Q) of generator settings in an exploratory probe on seeds 1–4, used to choose the grid.
- The smoke run (seed 11, 4 texts, 2 settings) showed Q3 values: matched generator err10_position_s11 3.63 and
  random_morphhi_s11 1.50; matched Bibles hrv 47.9, slk 34.6 (plus eng-kjv 10.9, Culpeper 16.6, out of band).
  These are in the real run (same seeds), so the direction for these four is already known.
