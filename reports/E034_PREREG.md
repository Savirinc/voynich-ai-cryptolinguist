# E034 pre-registration (ledger test 5): practical, list-type texts on E033's 8 features

Written 2026-10-21, before the run. Script: `experiments/e034_genre_features.py`. Updates `reports/LEDGER.md`.

## Question
E033: no Bible combines Voynich's three habits:
1. word repeats (R);
2. a rich vocabulary (types, hapax);
3. a flat Zipf head (C11).

The best-surviving L story is a rich-vocabulary language written as a *practical, list-type text*, where grammar
words are weaker. Do such texts close the gap?

## Texts (fixed now; inclusion decided by availability and length, before any feature was computed)
| Pool | Contents | Words | DEV-size windows |
|---|---|---|---|
| LAT_PRACTICAL | Apicius (recipes) 1–5 + Cato *De agri cultura* + Varro *Res rusticae* 1–3 | 58,900 | 2 |
| LAT_COLUMELLA | Columella *Res rustica* 1–12 + *De arboribus* | 115,100 | 3 |
| ENG_HERBAL | Culpeper, *The Complete Herbal* (1653), PG #49513, a plant-by-plant herbal | ~250,000 | up to 10 |

All Latin Library files are pooled in the order listed. Words are lowercase letter runs. The output records sha256
values.

**Considered and left out:**
- *Apicius* alone (23,400 words) is shorter than one DEV window, so it is pooled.
- *The Forme of Cury* (c. 1390, PG #8102): the recipes are interleaved with an 18th-century editor's preface,
  footnotes and glossary, and no clean rule separates them.
- No medieval Latin, Italian or German herbal is available in our corpora. That gap is stated, not filled.

## Features and rule
- **Features:** E033's 8, which do not depend on spelling: R, types, I_word, top_word, PERS_30, COV_30, type_hapax,
  zipf_slope. The code is E033's.
- **sd per feature:** the largest of:
  - the text's own window sd, if it has at least 3 windows;
  - the median window sd of the 12 E033 Bibles (as stored, already floored);
  - 2% of |Voynich|;
  - 0.01.

  The Bible median keeps texts with few windows from getting an unfairly tiny sd.
- **Fail:** |z| > 3.

| Outcome | Rule | Bayes factor |
|---|---|---|
| A PRACTICAL TEXT MATCHES | the best pool fails at most 1 of 8 | L × 3 |
| NO MATCH | otherwise | none |

A failure gives no factor against L. E033 already showed that Bibles do not match. That practical texts fail too
adds little new evidence, and this is stated in advance rather than chosen afterwards.

## What was seen before writing this (disclosed)
- Word counts of the pools.
- The heading structure of *The Forme of Cury*, used to decide whether to include it.
- No feature has been computed for any of these texts.
