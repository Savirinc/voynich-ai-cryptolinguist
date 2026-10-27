# E086: are the spaces mechanical, and is each line its own record? SPACES MECHANICAL; LINES INDEPENDENT

Run 2026-10-27 under `E086_PREREG.md` (locked). Script `experiments/e086_spaces_and_lines.py`; results
`experiments/results/e086.json`, log `e086_run.log`. Arham's road 2. Measurement; no ledger factor.

## Part A: where the spaces go is almost fixed by the glyphs around them
PRED = how much of the uncertainty "space here or not" is removed by knowing 2 glyphs on each side (0 = none, 1 = all).
| Text | PRED | space rate |
|---|---|---|
| **Voynich** | **0.673** | 0.185 |
| Naibbe cipher of Latin (spaces mechanical by design) | 0.666 | 0.165 |
| copy generator 31 / 32 | 0.538 / 0.574 | 0.195 |
| Indonesian (highest language) | 0.502 | 0.158 |
| English, German, Hungarian, Italian, Turkish, Latin, Czech | 0.452–0.225 | |
| Hebrew, Arabic (consonants; lowest) | 0.132 | |
Languages 0.132–0.502 (mean 0.319, sd 0.127). **SPACES MECHANICAL**: Voynich's spaces are more predictable from the
neighbouring glyphs than in every language, and exactly as predictable as in a verbose cipher whose spaces are set by
its tables.

## Part B: the next line does not continue the previous one
Cross-line pair (last word of a line → first word of the next line) scored against random other lines of the same page.
| Text | z | |
|---|---|---|
| 10 languages | +26.1 to +45.5 | sentences run on across lines (VALID) |
| Naibbe cipher of Latin | +6.33 | the cipher weakens but keeps continuity |
| **Voynich** | **+0.21** | the next line is no more connected than a random line of the page |
| copy generator 31 / 32 | +0.46 / −0.13 | |
Voynich's within-line pairs are slightly more predictable (−7.67) than its cross-line pairs (−7.78 real, −7.78
shuffled). **LINES INDEPENDENT (record-like).**

## What it means
- **The space is part of the glyph system**: it falls where the glyph rules put it (after the endings *-y, -n, -l, -r*,
  never before *e*). Every attack so far (E049–E084) treated each space as a word division. If the spaces are a
  writing rule, the true units may be different from the "words" we attacked.
- **Each line stands alone.** In every language the first word of a line follows on from the last word of the line
  before; in Voynich it does not. Voynich lines behave like separate entries (a list, a table, records, or verse lines
  that do not run on), or like a process that works line by line (as the copy generator does).
- A verbose cipher of continuous prose matches the spaces (Part A) but not the line independence (Part B): a cipher
  would have to be of a text whose lines are separate, or must break the line connection itself.
- Pre-registered consequences: the attacks are repeated with spaces removed (the decoder places its own word breaks),
  and decoders treat each line as a separate record.
