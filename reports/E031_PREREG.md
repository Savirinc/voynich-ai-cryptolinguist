# E031 pre-registration (ledger test 2): exact copies and near-copies together

Written 2026-10-21, before the run. Script: `experiments/e031_copy_pairs.py`. Updates `reports/LEDGER.md`.

## Question
In Voynich, neighbouring words are often exact copies (E030: 2.65× chance) and often near-copies, differing by one
glyph (3.64% of pairs). E030 found languages with frequent exact copies (Indonesian, Malay), but with almost no
near-copies (0.1%). Does any real language show **both habits in the same text**, each above chance?

- **M (copy-and-change writing)** produces both by its very mechanism: copy a nearby word, and sometimes change a
  glyph.
- **L** must find both in grammar: doubling for the exact copies, and something like agreement or rhyme for the
  near-copies.

## Statistics (per text)
- **R** = exact-repeat rate of neighbouring words ÷ Σ p_w² (as in E030).
- **NR** = near-copy rate of neighbouring words ÷ the same rate after randomly shuffling the words (mean of 5
  shuffles). Shuffling keeps word frequencies, so short words and small alphabets, which make near-copies common by
  chance, are corrected for. NR > 1 means near-copies are *attracted* to each other.
- **Near-copy** = edit distance exactly 1 (one letter substituted, inserted or deleted).

## Data
- **Voynich:** DEV prose, within-line pairs, clean tokens. Shuffles permute all tokens and refill the same line
  lengths.
- **Reference:**
  - the 14 E030 Bibles (10 primary, 2 secondary, 2 anchors);
  - every PG file in `data/raw/corpora/pg` with at least 10,000 words: 36 languages, including Tagalog, Ilocano,
    Cebuano, Welsh, Irish and Hebrew.
- **Sampling:** texts longer than 28,841 words give 10 random DEV-sized windows each; shorter texts are used whole.
  Seed 31031.

## What was seen before writing this (disclosed)
- Raw rates only: Voynich near 3.64%; the E030 Bibles' raw near rates (0.1–6.7%).
- NR has not been computed for anything, Voynich included.

## Decision and ledger update (fixed now)
- **Premise gate:** if Voynich NR < 1.5, its near-copies are not clearly attracted. The verdict is then PREMISE
  FAILS, with no update.
- Otherwise, a text "does both" iff R ≥ 1.5 **and** NR ≥ max(1.5, 0.67 × Voynich NR).

| Outcome | Rule | Bayes factor |
|---|---|---|
| A LANGUAGE DOES BOTH | at least one text does both | L × 3 |
| NO LANGUAGE DOES BOTH | none does | M × 3 |

**Why only weak factors (×3).** Under M, the likelihood of "both" rests on the *mechanism's design*, not on a
tested generator. Under L, about 50 texts in 36+ languages are a modest sample of the world's languages.

## Limits (stated in advance)
- A language that does both shows only that L *can* produce the pattern.
- None doing both shows only that our sample doesn't.
- The test that would put a real number on P(pattern | M), a tuned copy-and-change generator checked against all of
  C1–C10, comes after this.
