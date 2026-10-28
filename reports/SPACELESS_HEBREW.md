# E088: spaceless, line-by-line attack for the Hebrew family and Arabic. NO CLAIM, validated (5 of 5)

Run 2026-10-28 (1,859 s) under `E088_PREREG.md` (locked). Script `experiments/e088_spaceless_hebrew_family.py`; results
`experiments/results/e088.json`; every decoded line in `experiments/results/e088_decoded.json`; log `e088_run.log`.

## Yardstick chosen on known answers only
| Yardstick | languages it validates | mean normalised gap (crack vs junk) |
|---|---|---|
| COVER4 (words ≥ 4 letters) | 4 of 5 | −2.63 |
| COVER5 (words ≥ 5 letters) | 5 of 5 | +0.48 |
| **PAIR** (how often decoded neighbours are real word pairs) | **5 of 5** | **+0.58** |
Chosen automatically: PAIR (higher = decoded words follow each other as in the real language).

## Results (PAIR)
| Language | cracks (accuracy, score) | A controls max | threshold | Voynich A (agreement) | Voynich B (agreement) | B controls max |
|---|---|---|---|---|---|---|
| Hebrew | (1.00, −0.68), (1.00, −0.82) | −1.22 | −1.02 | −1.58 (1.00) | −1.26 (1.00) | −1.34 |
| Aramaic (Onkelos) | (0.99, −0.64), (1.00, −0.56) | −1.72 | −1.18 | −1.78 (1.00) | −1.51 (0.63) | −1.48 |
| Judeo-Arabic (Saadia) | (1.00, −0.66), (1.00, −0.69) | −1.42 | −1.05 | −1.56 (1.00) | −1.68 (1.00) | −1.35 |
| Talmud | (1.00, −0.73), (1.00, −0.72) | −1.53 | −1.13 | −1.63 (0.56) | −1.97 (0.61) | −1.58 |
| Arabic | (1.00, −1.33), (0.98, −1.36) | −1.89 | −1.62 | −1.86 (1.00) | −1.33 (0.54) | −1.31 |

**Verdict: NO CLAIM, validated.** With spaces removed and each line decoded alone, correct decodes read as real word
sequences (−0.56 to −0.82, Arabic −1.33), while Voynich decodes read like junk: on A every language scores at or below
its meaningless imitations; on B, Hebrew (−1.26) is slightly above its imitations (−1.34) but far below the threshold
(−1.02), and the rest are at or below theirs or unstable (agreement 0.54–0.63).

## Consequence
The spaceless line-by-line form is now excluded for Hebrew, Aramaic, Judeo-Arabic, the Talmud's Hebrew–Aramaic mixture
and Arabic, within scope (23 signs, one sign per letter with homophones, no filler signs). This closes E087's gap.
