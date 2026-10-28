# E092: do key facts survive another transcription or glyph cut? (approach check 3)

Pre-registration `E092_PREREG.md` (sha256 f64c5b9c…), script `experiments/e092_transcription_check.py` (sha256
5065c1ed…), results `experiments/results/e092.json`, log `e092_run.log`. Run 2026-10-28, 245 s.

## Result
| Fact | ZL (ours) | ZL, doubtful spaces joined | ZL, glyph groups as one symbol | Takahashi | Glen Claston (v101) | Status |
|---|---|---|---|---|---|---|
| F1 spaces mechanical (PRED > 0.502) | 0.673 yes | 0.665 yes | **0.425 no** | 0.681 yes | **0.424 no** | **DEPENDS ON TRANSCRIPTION** |
| F2 lines independent (z) | +0.13 | −0.72 | +0.13 | +0.80 | −0.59 | SURVIVES |
| F3 E067 gibberish-like vocabulary (T at 150) | 112.1 | 116.1 | 112.1 | 112.6 | 115.9 | SURVIVES |
| F4 E068 M ruled down (gibberish Voynich-like on 1 feature) | yes | yes | yes | yes | yes | SURVIVES |
| F5 E066 family-level repeats (z) | −1.05 | −0.76 | −0.21 | −1.04 | −0.69 | SURVIVES |

## What it means
- **Four of five facts are solid.** Lines are independent, vocabulary is gibberish-rich at 150 words, gibberish fails the
  shape battery, and repeats are family-level, whoever transcribed it and however the glyphs are cut.
- **"Spaces are mechanical" is not solid.** It holds when EVA letters are the units (ZL, Takahashi), and fails when the
  glyph groups are counted as single signs (our own S3 cut, and Claston's independent v101 alphabet both give 0.42, inside
  the language range 0.13–0.50). The two coarser cuts agree with each other. Much of the predictability seems to come from
  multi-glyph endings (-dy, -iin) that EVA spells out letter by letter. Caveat (disclosed before the run): with more
  symbols the 2+2 context is sparser, which by itself lowers PRED, and the language references are measured in their
  own letters, so neither cut is a perfect like-for-like.
- **Consequences.** E086's "spaces mechanical" moves from measured fact to "depends on the glyph cut". The spaceless
  attacks E087–E089 remain valid tests, but the fact that motivated them is weaker. No ledger factor rested on F1.
- **Ledger unchanged:** the three scored facts (E066, E067, E068) survive.
