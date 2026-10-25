# E070 pre-registration: do Voynich's content-like words have partners that persist across the book?

Written 2026-10-25, before the run. Script: `experiments/e070_content_partners.py`. Output: `experiments/results/e070.json`,
`e070_run.log`, report `reports/CONTENT_PARTNERS.md`. Updates `LEDGER.md`.

## Question
E069 found that Voynich's 200 commonest words keep weak partnerships across the book (0.073): above the copying
generator, below 56 of 60 languages, at the level of Hebrew, Polish, Slovak and Azerbaijani, whose commonest words are
grammar pieces. If Voynich's commonest words are grammar-like too, the partnerships that carry meaning should sit in the
**less common** words. This test repeats E069 on the words ranked 51–250 by frequency (the 50 commonest excluded).

## What is fixed in advance
- **Statistic:** E069's STAB (rank correlation of pair associations between the two halves, minus the within-half
  shuffle baseline), over the words ranked 51–250 that occur in both halves.
- **Texts, sizes, pseudo-lines, generator stretches:** exactly as E069 (Voynich ALL primary; A-only and B-only
  secondary; 60 Bibles; 10 generator stretches at each size). Seed 70070.
- **Gate:** ≥ 8 of 10 generator stretches below the languages' 10th percentile (ALL size), else VOID.
- **Fair bar:** the lower of (a) the languages' 10th percentile and (b) the median of the four grammar-heavy languages
  (hboWLC, polubg, slk, azb), the fair comparison for a text whose commonest words are grammar pieces.

| Outcome (primary, Voynich ALL) | Rule | Factor |
|---|---|---|
| **LANGUAGE-LIKE** | Voynich > every generator stretch and ≥ the fair bar | **L × 3** |
| **GENERATOR-LIKE** | Voynich ≤ the generator median | **M × 3** |
| INCONCLUSIVE | otherwise | none |

A-only must agree in direction (same rule at A size), else INCONCLUSIVE. Seed rule: Voynich within 0.05 of a boundary →
10 re-draws of languages and generator, ≥ 8 of 10 agree.

**Why this is not a second try at E069.** E069 asked about the commonest words and gave a declared one-attempt answer
(a draw). Its report named this follow-up as the sharpening; the word band, the bar and the rule are set here before
anything is measured. The two tests answer different questions (grammar-like words; content-like words) and only one
of them can move the ledger today: if E070 is also a draw, the partner family is closed.

## Disclosed
- E069's values for all groups on ranks 1–200 (Voynich 0.073; languages 0.011–0.215; generator 0.040–0.053; the four
  grammar-heavy languages 0.011–0.071).
- Nothing has been measured on ranks 51–250 for any real text. The statistic was smoke-tested on a toy language with
  60 function words and 300 topic words.
- One attempt (standing rule 9).
