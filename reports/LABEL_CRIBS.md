# E119: label words as name-cribs in paragraph-first lines (Arham, move 5)

Pre-registration `E119_PREREG.md` (sha256 745400ea…), script `experiments/e119_label_cribs.py` (sha256 e88e97b3…),
results `experiments/results/e119.json`, logs `e119_dev.log`, `e119_run.log`. Run 2026-11-01, 3 s.

## Question
If a label beside a drawing is a name, it should be introduced where names go: at the start of a paragraph. Do the
Voynich's label words stand in paragraph-first lines more than words of the same shape (first two letters) and frequency?

## Result
| Text | ENRICH (share in paragraph-first lines, label minus matched) |
|---|---|
| Culpeper (herb names) | **+0.054** |
| 10 planted generator texts | +0.193 to +0.231 |
| 70 nulls (60 copy-generator, 10 dice) | −0.043 to +0.028 (p90 +0.021) |
| **Voynich (222 label types)** | **−0.033** (bootstrap sd 0.017) |

- **The test works:** VALID, since every positive is above every null.
- **The Voynich:** its label words are, if anything, a little *less* common in paragraph-first lines than look-alike
  words. That puts it inside the null range and below its median.
- **Verdict NOT ENRICHED, M × 1.5.** It is well clear of the boundaries, so no seed check was needed.

| Label's section | ENRICH | Label types |
|---|---|---|
| Zodiac | −0.015 | 78 |
| Cosmological | −0.022 | 43 |
| Astro | −0.059 | 39 |
| Pharma | −0.074 | 25 |
| Bathing | −0.003 | 23 |
| Text | −0.074 | 12 |

None is positive. The paragraph-first share of label-word tokens is 0.165 on the label's own sheet and 0.160 on other
sheets (unscored).

## Reading
- The label words behave in the prose like any other word of their shape. They are not introduced at paragraph
  openings, as named things are in Culpeper.
- The paragraph-first surprise found in X117 is therefore not made of label names.
- **Limits:**
  - labels need not be names (they could be numbers, abbreviations or captions), hence only × 1.5;
  - a whole-word code whose prose never names the pictured things would also give this;
  - labels that never occur in prose (half of the label types) cannot be tested this way.

## Ledger
M × 1.5: **M 0.9210, L 0.0556, C 0.0105, O 0.0129** (was 0.8860 / 0.0803 / 0.0151 / 0.0186).
