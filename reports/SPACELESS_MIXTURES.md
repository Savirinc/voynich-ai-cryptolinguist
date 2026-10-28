# E089: spaceless line-by-line attack with mixed-language models. NO CLAIM, validated (7 of 7); seed check confirms

Run 2026-10-28 (2,314 s) under `E089_PREREG.md`; seed check E089b (179 s) under `E089B_PREREG.md`. Results
`experiments/results/e089.json`, `e089b.json`; decoded lines `e089_decoded.json`; logs `e089_run.log`, `e089b_run.log`.

## Yardstick (chosen on known answers only)
COVER4 validates 6/7 (gap +0.40); **COVER5 7/7 (+0.65), chosen**; PAIR 7/7 (+0.55).

## Results (COVER5: share of decoded letters inside dictionary words of ≥ 5 letters)
| Mixture | cracks (accuracy, score) | A controls max | threshold | Voynich A (agreement) | Voynich B (agreement) | B controls max |
|---|---|---|---|---|---|---|
| Hebrew + Aramaic | (0.97, 0.20), (1.00, 0.30) | 0.170 | 0.186 | 0.081 (1.00) | 0.093 (0.49) | 0.134 |
| Hebrew + Judeo-Arabic | (0.98, 0.18), (0.97, 0.18) | 0.133 | 0.156 | 0.104 (0.98) | 0.179 (1.00) | 0.188 |
| Hebrew + Aramaic + Judeo-Arabic | (0.97, 0.22), (1.00, 0.27) | 0.135 | 0.175 | 0.101 (1.00) | **0.172 (1.00)** | 0.114 |
| Hebrew (Latin letters) + Latin | (1.00, 0.33), (1.00, 0.35) | 0.103 | 0.219 | 0.065 (0.56) | 0.067 (1.00) | 0.070 |
| Hebrew (Latin letters) + Turkish | (1.00, 0.43), (1.00, 0.40) | 0.097 | 0.250 | 0.072 (1.00) | 0.108 (0.85) | 0.114 |
| Latin + German (comparison) | (1.00, 0.48), (1.00, 0.47) | 0.170 | 0.319 | 0.162 (1.00) | 0.198 (1.00) | 0.200 |
| Latin + Turkish (comparison) | (1.00, 0.53), (1.00, 0.55) | 0.177 | 0.353 | 0.124 (0.99) | 0.127 (1.00) | 0.228 |

**The one near miss:** Hebrew + Aramaic + Judeo-Arabic on Currier B, 0.172 against a threshold of 0.175, above its own
imitations (0.114). Rule 8 seed check (E089b): with 10 new seeds the same decode scored 0.096 nine times and 0.169 once;
**0 of 10 pass**. The 0.172 was one lucky search outcome. Its decoded text is mostly the commonest letters (א ל ו י ה מ)
with almost no long words, unlike the correctly decoded test text (ישראל, לעבידא, אלגוהר...).

**Verdict: NO CLAIM, validated.** The spaceless line-by-line form with mixed-language models is excluded for these
seven mixtures within scope.
