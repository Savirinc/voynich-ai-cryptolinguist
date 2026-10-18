# E025 pre-registration: methodology test A4 — does any system produce Voynich's line effects for free?

Written 2026-10-18, BEFORE the full run. Smoke (1 sample per family/language; Voynich not computed): V_first
0.04–0.07, V_last 0.03 for families without a line rule (0.15–0.23 for those with one), LEN_first 1.12–1.31
(line wrapping pushes long words to the next line), LEN_last ~1.0. No setting changed after it.

## Question
Voynich lines are known to behave differently at their start and end. Do any candidate systems produce that
without an explicit line rule? If none does, the line is a functional unit of the writing system (a scribal
convention or a line-based procedure), and every Stage B decoder must model it.

## Features (experiments/e025_line_effects.py)
Lines with >= 3 words. V_first / V_last: Cramer's V between position (initial or final vs medial) and the
first / last glyph. LEN_first / LEN_last: initial / final word length relative to medial.

## Families (20 samples each, DEV size; seed 25025)
word, compound, naibbe_noline (E014 naibbe spec with line-end m off): no line rule. naibbe_spec (E014 fitted line-end
m), rugg_rep, self_citation_rep: explicit line rule or line copying, reported for reference.

## Decision (fixed now)
A feature is produced FOR FREE by a family without a line rule iff |z| <= 3. Reported per feature.
- Nothing produces V_first or V_last for free → the line is a functional unit; Stage B decoders get a line model
  (line-initial and line-final transformations), validated on twins.
- Otherwise → the line effects follow from that family's word structure plus wrapping.
