# E034 (ledger test 5): practical, list-type texts — NO MATCH

Pre-registration: `reports/E034_PREREG.md` (sha256 cbbd173a…1fec, locked before the run). Script
`experiments/e034_genre_features.py`. Results: `experiments/results/e034.json`, `e034_run.log`.

## Plain-language result
Recipes, farming manuals and a herbal do **not** close the gap. The best pool, Apicius + Cato + Varro, fails 3 of 8:
- no word repeats (R 0.12 vs Voynich 2.65);
- *more* distinct words than Voynich (8,070 vs 6,077);
- a steep Zipf head (−0.80 vs −0.65).

Columella fails 5, and Culpeper's herbal fails 4. By the pre-registered rule: **NO MATCH**, and **no update**, as
stated in advance.

| Pool | Fails | R | types | hapax | Zipf | PERS_30 |
|---|---|---|---|---|---|---|
| **Voynich** | — | **2.65** | **6,077** | **0.68** | **−0.65** | **0.26** |
| Apicius + Cato + Varro | 3 | 0.12 | 8,070 | 0.64 | −0.80 | 0.38 |
| Columella | 5 | 0.02 | 9,810 | 0.67 | −0.83 | 0.58 |
| Culpeper's herbal | 4 | 0.03 | 2,970 | 0.45 | −0.88 | 0.57 |

## What it means
- **Genre is not the explanation**, at least not these genres. Practical texts don't repeat words, and their most
  common words dominate just as much as in prose.
- **The flat Zipf head (C11) is now unexplained by every text we have measured:** 12 Bibles, 3 practical texts and
  the copy generator. It is the most distinctive word-level fact we have.
- **The unexplained combination stands:** frequent exact copies, frequent near-copies, a rich vocabulary, and no
  dominant words.

## A possible explanation (a hypothesis, not tested)
One mechanism would produce all four at once: **variant spellings of the same word**, used freely.
- A common word written several ways splits its count across variants, so no word dominates (flat Zipf head) and
  there are more distinct words and rarer forms.
- A word next to a variant of itself becomes a near-copy.
- In a language that doubles words, both exact copies and near-copies follow.

This is one added part (spelling variation), and four measured facts call for it, so the Occam rule allows it. It
can be tested by adding spelling variation to a real text and checking all the features.
