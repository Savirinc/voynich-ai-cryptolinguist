# E092 pre-registration (approach check 3 of 4): do key facts survive another transcription or glyph cut?

Written 2026-10-28, before the full run. Script: `experiments/e092_transcription_check.py`. Output:
`experiments/results/e092.json`, `e092_run.log`, report `reports/TRANSCRIPTION_CHECK.md`. Updates `LEDGER.md`.

## Question
Every test used one transcription (ZL 3b, EVA) and its word spaces. Do our key facts hold if a different person
transcribed the manuscript, if the uncertain spaces are read the other way, or if the glyphs are cut into different
letters?

## Data (DEV only: prose; LOCKED_TEST leaves excluded with the ZL leaf list)
| Variant | What changes |
|---|---|
| ZL | baseline (the project's transcription) |
| ZL_J | ZL, uncertain spaces (',') removed: both sides joined |
| ZL_S3 | ZL, every S3 unit (ch, sh, cth, ckh, cph, cfh, iin, in, ir, ee, qo, dy …) written as one symbol |
| IT | Takahashi, voynich.nu `IT2a-n.txt` (sha256 7f27a8b0…), own readings and spaces, EVA |
| GC | Glen Claston, voynich.nu `GC2a-n.txt` (sha256 b09570cb…), v101 alphabet (a different glyph cut, 70 symbols), own readings and spaces; a word is unclean if it has ? @ [ ] { } < > ; |
Downloaded 2026-10-28 into `data/external/transcriptions_e092/` (untrusted data; read with `python -I`).

## Facts and rules (each with the original experiment's own functions and judge; only the Voynich text is swapped)
| Fact | Measure | Conclusion kept iff |
|---|---|---|
| F1 spaces mechanical (E086) | PRED | PRED > max language PRED (stored E086: 0.502) |
| F2 lines independent (E086) | continuity z | z < min language z / 2 (stored: 26.1 / 2) |
| F3 vocabulary richness (E067, M×3) | E067 judge, references recomputed with E067's seed, E067 seed rule | verdict unchanged |
| F4 small-scale battery (E068, M×1/3) | E068 judge, references recomputed with E068's seed, E068 seed rule | verdict unchanged |
| F5 family-level repeats (E066, M×1.4) | E066 judge with stored generator z, E066 seed rule | verdict unchanged |
Per fact: **SURVIVES** (all 4 variants agree with ZL), **FRAGILE** (1 disagrees), **DEPENDS ON TRANSCRIPTION** (≥ 2).

## Ledger
A scored fact (F3 E067, F4 E068, F5 E066) that DEPENDS ON TRANSCRIPTION has its factor withdrawn (set to 1). FRAGILE
is reported, no change. F1/F2 carry no factor; their status is recorded in the measured facts. If the ZL baseline does
not reproduce a published conclusion, that fact is VOID here.

## Disclosed (seen before locking)
- The script, with these rules, was written first; then a smoke run (`--smoke`: ZL and GC only, E067/E068 language
  references cut to 2 windows per language, 20 bootstraps) was read. Deterministic parts are therefore known:
  ZL PRED 0.673 MECHANICAL, z +0.13 INDEPENDENT, E066 z −1.05 FAMILY-LEVEL; **GC PRED 0.424 (NOT MECHANICAL)**,
  z −0.59 INDEPENDENT, E066 z −0.69 FAMILY-LEVEL. With the cut references, ZL and GC both gave the published E067 and
  E068 verdicts. Variant sizes: ZL 28,841 tokens / 6,077 types / 68% one-offs; ZL_J 26,810 / 6,876 / 71%; IT 28,555 /
  6,132 / 68%; GC 30,194 / 7,230 / 70%.
- Seen caveat, not acted on: PRED uses a 2+2 symbol context; with 70 symbols (GC) contexts are sparser, which by itself
  lowers PRED. The rule is not changed; the report will discuss it.
- Baseline z and E066 z differ slightly from the published values (+0.21, −1.17) because the random draws are consumed in
  a different order; the conclusions are the same.
