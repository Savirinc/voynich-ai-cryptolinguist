# E108 amendment (before any labelling or analysis), 2026-10-31

**Problem.** The locked labelling grids show each crop with a margin, so the detected component's boundary is not
visible. In Voynich script the gallows foot often joins the next letter, which makes the prereg's G (single gallows)
versus M (merged blob) distinction unreliable. That distinction decides which shapes are analysed.

**Fix.** `experiments/e108_grids_v2.py` redraws the same crops, with the same grid and cell numbers and the same
shuffle, at 160 px, with the detected component tinted red. Labelling uses these v2 grids. Nothing else changes: the
locked script's `analyze` stage, the labels file and the rules are untouched.

**State when written.** One v1 grid (grid 1) had been viewed. No label has been written, and no feature, record or
analysis output has been looked at.
