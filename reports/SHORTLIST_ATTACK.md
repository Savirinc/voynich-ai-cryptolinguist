# E052: the validated attack on the rest of the shortlist plus Romani — all VALIDATED, NO CLAIM

Pre-registration `reports/E052_PREREG.md` (sha 8664ef61…7c28, commit 9814a2f). Script
`experiments/e052_shortlist_attack.py`. Results: `experiments/results/e052.json`, `e052_run.log`.

lexrate is the share of decoded words that are real words in the language model's vocabulary.

| Language | Known-answer cracks (accuracy / lexrate) | Highest control (generator, pseudo-Voynich) | Threshold | **Voynich A** lexrate | Result |
|---|---|---|---|---|---|
| Czech | 0.999 / 0.72; 1.000 / 0.82 | 0.349 | 0.536 | **0.214** | validated, no claim |
| Serbian-Croatian | 1.000 / 0.75; 1.000 / 0.75 | 0.305 | 0.528 | **0.257** | validated, no claim |
| Slovak | 0.999 / 0.73; 0.999 / 0.73 | 0.276 | 0.503 | **0.250** | validated, no claim |
| Ukrainian | 1.000 / 0.72; 1.000 / 0.71 | 0.348 | 0.529 | **0.246** | validated, no claim |
| Romanian | 1.000 / 0.86; 1.000 / 0.82 | 0.507 | 0.662 | **0.405** | validated, no claim |
| Italian | 1.000 / 0.83; 1.000 / 0.80 | 0.344 | 0.574 | **0.332** | validated, no claim |
| Romani | 1.000 / 0.85; 1.000 / 0.82 | 0.373 | 0.598 | **0.351** | validated, no claim |

**Verdict (pre-registered): NO CLAIM.**
- Every language was validated: the method read real text in a Voynich-like script perfectly and separated it clearly
  from all fakes.
- In every language, Voynich A decodes **no better than the fakes**, and usually worse than the best fake.

## Absence rule
- **Searched slice of L:** 0.35 × (Czech 0.08 + Serbian-Croatian 0.05 + Slovak 0.03 + Ukrainian 0.04 + Romanian 0.03 +
  Italian 0.15 + Romani 0.03) = **0.1435**.
- **Update:** L × (1 − 0.1435 × 0.8) = **× 0.885**.
- **New values:** **M 0.0074, L 0.965, C 0.0263, O 0.0012.**

## Cumulative "searched, not found" (VOY23 class: letter by letter, up to 23 signs, homophones, spelling slips)
Hebrew, Turkish, Latin, Czech, Serbian-Croatian, Slovak, Ukrainian, Romanian, Italian and Romani: **10 languages.**
Together they were 0.38 + 0.41 = **0.79 of the L-alpha-known form** (a known language written letter by letter). That
form is now largely searched, with nothing found.
