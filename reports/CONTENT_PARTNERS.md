# E070: do Voynich's content-like words have partners that persist across the book? — INCONCLUSIVE by rule; in substance, no partners at all

Pre-registration `reports/E070_PREREG.md` (sha256 1f1b48a6…daeedc), amendment `E070_AMENDMENT.md` (statistic replaced
before any real measurement, sha256 b6f8ca83…d6ab2c), script `experiments/e070_content_partners_v2.py` (sha256
ac52e752…aea6e33). Results `experiments/results/e070.json`, `e070_run.log`. 4.5 min.

## Verdict
Gate passed (8 of 10 generator stretches below the languages' 10th percentile). **Voynich ALL: PSO 0.004**, below the
generator median (0.027) and below every one of the 60 languages (min 0.018): the primary rule says GENERATOR-LIKE. The
pre-registered safeguard then asks Currier A alone to agree (A ≤ its generator median): A is 0.009 against a generator
median of 0.008, a hair above, so the verdict is **INCONCLUSIVE (A-only does not agree)**. The seed rule (10 re-draws)
returned INCONCLUSIVE 9 times and GENERATOR-LIKE once. **No factor.** The partner family is closed, as declared.

**Plain reading.** Among Voynich's content-like words (ranks 51–250), 423 pairs are partners in the first half of the
book and 453 in the second; **only 15 are partners in both**, and shuffling the words gives 13. Voynich's less common
words have no friendships that carry across the book. Every one of the 60 languages has some (Baatonum 0.14, Kikuyu,
Indonesian and Khumi Chin 0.12 … Hungarian 0.02); the copy generator has a few (0.01–0.05) from its long-range copying.
Inside Currier A alone: 1 pair of 112 persists (shuffled gives about 0). Inside B: 7 of 548 (shuffled about 6).

## Numbers
| Text | PSO (overlap − shuffled) | Partners half 1 / half 2 / both | Shuffled partners (each half) |
|---|---|---|---|
| **Voynich ALL** | **0.004** (raw 0.017) | 423 / 453 / **15** | about 373 |
| Voynich A only | 0.009 (raw 0.009) | 52 / 61 / 1 | about 39 |
| Voynich B only | 0.005 (raw 0.013) | 261 / 294 / 7 | about 245 |
| 60 languages, ALL size | min 0.018, 10th pct 0.036, median 0.058, max 0.142 | | |
| Grammar-heavy four (Hebrew, Polish, Slovak, Azerbaijani) | 0.029, 0.069, 0.072, 0.060 | | |
| Generator, ALL size | median 0.027, max 0.047 | | |
| Languages, A size | 10th pct 0.014, median 0.052 | | |
| Generator, A size | median 0.008, max 0.019 | | |

## Why the rule did not score what the numbers show
The A-only safeguard was written to protect against the A→B dialect shift making the whole-book value look
generator-like for a non-meaning reason. It did its job literally: A alone is not *below* the generator median, it is
*at* it (0.009 vs 0.008). A alone is also far below its languages (10th percentile 0.014, median 0.052). So A agrees
that Voynich is not language-like, but not, by a hair, that it is generator-like. The rule is applied as written.

## What this means, and the one alternative that must be named
- **Lean towards M, unscored.** On the second grammar-shape test aimed at the unrecorded-language form, Voynich's
  content-like words behave as if no two of them belong together across the book. Together with E066 (no word
  personalities in repeating) and E069 (common words with only weak partnerships), the picture is of a text whose
  individual words carry no persistent association, which is what a meaningless process gives.
- **The alternative: a catalogue.** A herbal in which every page describes a different plant, with its own names and
  properties, would also give no cross-book partners among content words, because each entry's vocabulary is local.
  Bibles are the wrong comparison for that; a herbal, a pharmacopoeia or a recipe book is the right one. Culpeper's
  herbal is on disk; the Gaskell & Bowern technical texts (Leechbook, Materia Medica, Pliny) are too. This was not
  pre-registered and is not scored here. It is the next question if the work stays inside L: *does a real catalogue
  text also lack persistent content partners?* If it does, E069–E070 say nothing against L-as-catalogue; if real
  catalogues keep partners (plant → "root", "water", "boil"), Voynich's zero is a real anomaly for L.
- Ledger unchanged: M 0.0739, L 0.8939, C 0.0281, O 0.0041.
