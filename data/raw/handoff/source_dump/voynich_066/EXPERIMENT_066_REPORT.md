# Voynich Experiment 066: Context specificity and split-zodiac semantic probe

**Date:** 2026-10-14. **Status:** structural prediction demonstrated; semantic reading NOT established.

## Source
User-supplied ZL3b-n IVTFF EVA v3b (2025); Experiment 064 conservative clean token index, 33,007 tokens (32,132 prose; 875 labels). No phonetic assumptions about EVA. Five-fold physical-leaf test; specific candidate `qo...` / `o...` form pairs. Sample of 8,821 comparable prose occurrences on 99 leaves (excluded examples lacking a transcribed preceding word).

## Question 1: What predicts initial q?

All models already know current observable word's shared stem, first/last three glyphs, Currier variety, section and position in line. Adding context yields these held-out log losses (nats per eligible occurrence):

| Features | Log loss |
|---|---:|
| Current stem + section + layout | 0.61860 |
| + previous word's final glyph | 0.56112 |
| + previous word's final two glyphs | 0.55839 |
| + preceding full word | **0.55127** |
| + second previous word's final glyph | 0.55189 |

Cluster-bootstrap (1,000 resamplings of physical leaves) interval for per-occurrence improvement of full previous word over single previous final glyph: 0.0059–0.0138 nats. Stronger context helps but additional history didn't help; cannot distinguish grammatical dependence from cipher or specialized notation. Vocabulary-eligibility criteria selected using entire corpus, so this is exploratory rather than completely untouched model selection; the actual classifier was trained on disjoint physical leaves. No word meanings recovered.

## Question 2: Do paired Aries/Taurus panels share sign-specific label vocabulary?

Use the 319 clean label tokens on the twelve surviving zodiac panels. Compare distributions of 2- and 3-character initial EVA chunks with Jensen-Shannon divergence (bits; lower means more alike). Both same-sign pairs were relatively close across all 66 panel comparisons:

- Aries f70v1/f71r: distance **0.3291 bits**, rank **8/66** (1 = closest).
- Taurus f71v/f72r1: distance **0.3636 bits**, rank **14/66**.
- The mean distance of these two pairs = **0.3463 bits**; a naive random matching among all twelve panels yields exploratory **p≈0.043**.

**Crucial restricted control:** Those split-sign panels are all smaller than most other zodiac panels. Among just those four panels, there are only **3** different ways to form two disjoint pairs. The real same-sign matching is the closest but its exact restricted p-value is **1/3**, not significant. The closest overall pair is **f70v1 with f70v2**, which represents two DIFFERENT signs on the same physical leaf (0.2655 bits). This means local manuscript organization/scribe/proximity remains a confound. **No same-sign vocabulary or image-to-word semantic link established.**

## Decisions

- RETAIN: q selection is responsive to specific preceding vocabulary beyond only a previous final character. Stronger context model is warranted, but not necessarily a transformer.
- WATCHLIST: Similarity between two-part zodiac panels is worth closer controlled examination. It has not survived adequate size/proximity controls.
- DO NOT CLAIM: `q` is a negation, article, tense marker, or command; `otral` means March; month/sign labels have been deciphered; identical degree numbers across signs recovered; any medieval language ranks above others.

## Near-term decisive test

Secure pixel coordinates and individually validated label-to-figure matching for 30 zodiac-degree entries from two complete signs. Select the glyph-order direction before language tests. Hold out one entire sign. Independently code visual attributes without exposure to its labels. Test whether learned word components predict unseen visual attributes after controlling for ring, sign, proximity, and textual register. Separately, compare against dated Old French/Occitan/Latin corpora under explicitly capacity-limited transliteration and cipher assumptions. These historical corpora were not available in this run; do not infer linguistic ancestry from EVA substrings.

## Reproduction

`python voynich_experiment_066.py` from a working environment containing `/mnt/data/voynich_tournament_064/indexed_clean_corpus.csv`. Requires numpy, pandas, scipy, scikit-learn. See results.json and associated CSVs. Parsing choices, feature selection and hypothesis comparisons are pre-specified in the script; all exploratory language hypotheses remain open.
