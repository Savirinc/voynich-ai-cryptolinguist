# E053: abbreviated Latin (technical and sacred) — both VALIDATED, NO CLAIM

Pre-registration `reports/E053_PREREG.md` (sha fe9fc106…196a, commit f63c2bd). Script
`experiments/e053_abbrev_latin.py`. Results: `experiments/results/e053.json`, `e053_run.log`.

| LM (Gaskell & Bowern abbreviated Latin) | Mean word length | Known-answer cracks (accuracy / lexrate) | Best control | Threshold | **Voynich A** |
|---|---|---|---|---|---|
| Technical (Pliny) | 5.0 | 0.999 / 0.70; 0.999 / 0.74 | 0.324 | 0.513 | **0.238** |
| Sacred (Vulgate NT) | 4.2 | 0.998 / 0.65; 0.999 / 0.63 | 0.380 | 0.505 | **0.348** (agreement 0.22) |

**Verdict (pre-registered): NO CLAIM.** Both abbreviation LMs were validated: real abbreviated Latin in a Voynich-like
script was read perfectly. Voynich A decodes no better than the fakes under either.

**Absence rule:** L × (1 − 0.15 × 0.40 × 0.7) = × 0.958, giving **M 0.0077, L 0.963, C 0.0274, O 0.0013.**
