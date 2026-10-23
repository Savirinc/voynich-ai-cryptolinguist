# E045 pre-registration: does human-written gibberish avoid identical neighbours? (C21 against hypothesis M)

Written 2026-10-23, before the run. Script: `experiments/e045_human_gibberish.py`. Updates `reports/LEDGER.md`.

## Question
C21 (E043/E044): Voynich doesn't avoid putting a word right next to an identical word (AS ≈ 1). Every ordinary text
and writing system we tested avoids it (AS 0.00–0.53). The copy generator reaches 0.76.

**Do people writing meaningless text by hand avoid it, as real writers do, or not, as Voynich doesn't?** This is the
fair test of C21 for M, following the rule "don't rule out gibberish".

## Data
- **Source:** Gaskell & Bowern (2022), github.com/danielgaskell/voynich, commit d076a7d0 (code and gibberish data
  under a modified MIT licence).
- **Gibberish:** 38 transcriptions written by human volunteers, about 10,100 words in total, median 272 words each.
- **Meaningful:** the authors' 72 texts (modern, historical and constructed languages; scripture and technical),
  all with their own line breaks.
- **Voynich:** Currier A and Currier B, raw EVA, clean tokens, own lines.

## Statistic: AS, with an exact expectation (not shuffles)
- **Per line:** the expected number of identical neighbour pairs, if the line's own words were in random order, is
  E = Σ n_w(n_w − 1) ÷ L. The observed number is O.
- **AS = ΣO ÷ ΣE.** Lines of fewer than 2 words, and separator lines made only of _ or -, are skipped.
- **Gibberish:** pooled across writers, because single samples are too short (most have E < 3). The 95% interval comes
  from resampling writers (2,000 draws, seed 45045).
- **Meaningful:** AS for each whole text. Texts with E ≥ 5 form the reference distribution.

## Decision
| Outcome | Rule | Factor |
|---|---|---|
| HUMAN GIBBERISH LIKE VOYNICH | Voynich A's AS lies inside the gibberish 95% interval, **and** fewer than 5% of meaningful texts (E ≥ 5) have AS ≥ 0.85 | M × 3 |
| HUMAN GIBBERISH AVOIDS ADJACENCY | the upper end of the gibberish interval < 0.75 | M × 1/3 |
| INCONCLUSIVE | otherwise | none |

**Why only ×3.**
- The volunteers were modern people writing briefly, not 15th-century scribes producing about 240 pages.
- The samples are short.
- The rule also requires meaningful texts to *rarely* reach Voynich's level. Without that, a match would show only
  that both groups can do it.

## What was seen before writing this (disclosed)
- **The repository's README** (abstract), which reports that gibberish has higher repetition of words and characters,
  including triple repeats. That is relevant and is disclosed: it makes HUMAN GIBBERISH LIKE VOYNICH more likely, and
  the rule was not changed because of it.
- **The size of each sample, and the *expected* counts E** (to check whether single samples could be scored; they
  can't). No observed count O, and no AS, has been computed for any gibberish or meaningful text.
