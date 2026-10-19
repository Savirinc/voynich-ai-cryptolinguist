# E026 pre-registration: does Voynich have a compact ending inventory written with its own glyphs?

Written 2026-10-19, BEFORE the full run. Smoke run (1 sample per family at DEV size; Voynich NOT segmented, no
Voynich statistic computed). Twin means: word DIST 0.23 / NSUF95 82; Voynich-glyph twins DIST 0.34–0.51 (rugg 0.51,
NSUF95 19); cmp_marked split accuracy 0.971, DIST 0.95; cmp_random split 0.766, DIST 0.22. No setting changed after
the smoke run.

## Question
Stage B development (reports/STAGE_B_DEV.md, 2026-10-19) showed that a stem + ending notation can be read from the
cipher alone if its endings are written recognisably, with glyphs of their own. Does the unsupervised segmenter find
such an ending inventory in Voynich? And which family's ending structure does Voynich match?

## Data
- **Voynich:** DEV prose clean tokens (`E.voynich_lines()`, LOCKED_TEST excluded): 28,841 words, and the Currier B
  subset (19,490). Raw EVA characters are the glyphs.
- **Twins:** every E021 family, generators unchanged, 10 samples × la/it/fr/de per language family and 20 per
  generator, at both sizes.
- **New controls:** 20 each, from la text. Latin stem + inflectional ending (fixed list, as in the dev probes), coded
  injectively in EVA letters:
  - *cmp_marked:* endings use y d n l r m, stems use the other 14 letters (positive control);
  - *cmp_random:* stems and endings share all 20 letters (unmarked control).

## Procedure
`experiments/e026_endings.py`, seed 26026. Segmenter `vcl.solvers.segment.segment_types` with max_suf 4,
min_stem 2, a_s 1, a_f 1e-6, 120 sweeps annealed from T 3 to 0.05, smooth 0.01, start from no splits.

Features (`ending_features`):

| Feature | Definition | Role |
|---|---|---|
| SPLIT | Share of tokens given a non-empty suffix | Decision |
| NSUF95 | Number of suffix types covering 95% of suffixed tokens | Decision |
| DIST | Total-variation distance between the glyph distributions of the suffix lexicon and the stem lexicon | Decision |
| PAR | Share of word types whose stem has ≥ 2 suffixes | Reported only |

## Positive control and power (rules 3 and 9), at each size
**Gate:** cmp_marked split accuracy ≥ 0.95 in ≥ 90% of samples, **and** a DIST separation between cmp_marked and
cmp_random ≥ 3 pooled sd. If the gate fails, that size's verdict is VOID.

## Decision rule (fixed now)
1. **MARKED ENDINGS** iff Voynich DIST > the 95th percentile of the `word` family (real la/it/fr/de spelling) **and**
   Voynich NSUF95 ≤ that family's 95th percentile. Otherwise NOT MARKED.

   *Reading:* Voynich writes its endings more distinctly than ordinary alphabetic spelling, as a usable compound
   notation would. Glyph-built twins (Naibbe, Rugg, self-citation) may also pass this rule. That is why
   MARKED ENDINGS is evidence about the **notation**, not about meaning.
2. **Family match:** a family is CONSISTENT iff |z| ≤ 3 on SPLIT, NSUF95 and DIST (sd floors 0.01, and 1.0 for
   NSUF95). Reported for DEV and B.
3. **Descriptive:** the top-25 Voynich suffixes and their token shares are reported. They are structure only, with
   no reading.

## What would change our mind
NOT MARKED, or Voynich consistent only with unmarked families, would argue against a readable stem + ending notation
with distinct ending glyphs. Stage B would then move to other unit maps (whole-word codebook, B1 learned tables).
MARKED ENDINGS together with consistency with compound/marked families keeps the compound route first.
