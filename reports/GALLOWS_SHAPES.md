# E108 (Arham): do the scribes draw gallows differently, and are word-initial gallows drawn larger (calligraphy)?

- **Pre-registration:** `E108_PREREG.md` (sha256 5cda4f04…), commit cd11330.
- **Amendment:** `E108_AMENDMENT.md` (labelling grids with the detected shape tinted red), before any labelling.
- **Scripts:** `experiments/e108_gallows_shapes.py`, `e108_grids_v2.py`, `e108b_seed_check.py`.
- **Labels:** `reports/data/e108_labels.csv`, committed before analysis (f08ffb1).
- **Results:** `experiments/results/e108.json`, `e108b.json`.
- **Images:** 37 allowed full-resolution single-page canvases (no LOCKED_TEST leaf, no f102).

## Labels (blind: shuffled crops from all pages)
| Label | Count |
|---|---|
| G: single gallows | 419 |
| B: bench gallows (drawn across *ch*) | 98 |
| M: gallows merged with other letters | 158 |
| N: not a gallows | 489 |
| U: unsure | 88 |

## 1. Do the scribes draw gallows differently? WEAK (pre-registered verdict)
- **Classifier result:** page-by-page, a simple classifier using five shape measures (height, width, slant, ink
  fill, loops) names the scribe correctly for 48% of 31 pages, against 32% by chance. Permutation p is 0.016, so the
  verdict is WEAK.
- **Herbal pages only** (secondary; section held fixed; scribes 1, 2 and 5): 71% correct against 43% by chance,
  p 0.010.
- **Rule 8 check (E108b):** omitted from the prereg and run before reporting. Over 10 seeds, p ranged 0.007–0.015 for
  all pages (5 of 10 below 0.01) and 0.008–0.012 for herbal (4 of 10). The true p is about 0.01, so the verdict stays
  WEAK.

| Scribe | Pages | Gallows | Height (x-heights) | Width | Slant (degrees from upright) | Loops |
|---|---|---|---|---|---|---|
| 1 | 6 | 65 | **3.35** | 2.39 | **−13** | 0.51 |
| 2 | 9 | 109 | 3.01 | 2.47 | −23 | 0.46 |
| 3 | 10 | 182 | 2.90 | 2.25 | −22 | 0.70 |
| 5 | 6 | 63 | 3.24 | 2.62 | −19 | 0.43 |

Scribe 1 draws taller, more upright gallows, and scribes 2 and 3 lean them more. This is modest evidence of personal
style, in line with Davis (2020).
- **Caveats:** scribe 3 appears only on star pages, so scribe and section are mixed in the all-pages test. Scribe 1
  has only 6 usable pages. The labelling is mine.

## 2. Are gallows drawn larger at the start of a word? NOT LARGER AT WORD START (pre-registered verdict)
Across 26 pages, word-initial gallows compared with gallows inside words:

| Measure | Median change | p | Required |
|---|---|---|---|
| Width | **+10.6%** | 0.0095 | p < 0.005 and ≥ 10% |
| Height | +3.3% | 0.047 | |

Width reaches the 10% size but misses the strict p threshold. The verdict is NOT LARGER, with a lean towards slightly
wider gallows at word starts.

**Unscored:** gallows at the **start of a line** (including paragraph capitals) are 17% taller and 41% wider than
gallows inside words. The flourish is strong at line and paragraph starts and weak at ordinary word starts.

## 3. Bench gallows (descriptive)
Gallows drawn across *ch* rise higher than plain ones (3.49 vs 3.05 x-heights). They are much wider (3.6 vs 2.4, which
includes the *ch*) and have more loops (1.3 vs 0.6). The bench gallows is a larger, more elaborate form, not a plain
gallows dropped onto *ch*.

## Ledger
No factor (pre-registered). M 0.7422, L 0.1816, C 0.0342, O 0.0421.
