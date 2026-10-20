# E028 pre-registration: Occam rung 1 at the word level

Written 2026-10-20, before the run. Script: `experiments/e028_syllable_words.py`. Follows `reports/OCCAM.md` and E027.

## Question
E027 found that Voynich's glyph statistics (with glyph groups read as units) are inside the range of plainly
written simple-syllable languages. Is the same family consistent with Voynich at the **word** level?
- **Topic clustering of word types** (E019): I_word, top_word.
- **Persistence of the 30 most common types** (E021): PERS_30, COV_30.

If not, the plain rung-1 hypothesis fails on facts it must also explain.

## What this test can and cannot do (stated in advance)
- Our meaningless generators, Rugg and self-citation, were already rejected on these statistics (E019, E021). So
  this test does not newly separate "language" from "gibberish". It asks whether rung 1 is consistent with *every*
  fact so far.
- Voynich's values were already published before this was written (`UNIT_BURSTINESS.md`, `PERSISTENCE.md`):
  - DEV: I_word 0.387, top_word 0.285, PERS_30 0.264, COV_30 0.917.
  - The no-Voynich calibration (`experiments/results/smoke/e028_calib.json`) was run first.
  - The decision rule below was written into the script **before** the calibration ran, and is E021's rule. It was
    not changed afterwards.

## Data and sampling
- **Texts and sha256:** the E027 Bibles (see `E027_PREREG.md`).
- **Tokens:** words for haw1868, ton, mri2012 and vie1934. For vie1934 that means syllables, since Vietnamese
  writes a space after each syllable. Mandarin uses pinyin syllables *with* tone digits; toneless pinyin is
  reported only.
- **Anchors:** latVUC and eng-kjv words.
- **Sampling (E019 design):** each Bible, in canonical book order, is cut into 4 equal quarters. A sample takes one
  random contiguous window of N/4 + 1 tokens from each quarter. That gives 10 samples per text, at DEV size
  (28,841) and Currier B size (19,490). Seed 28028.
- **Features:** E019's `burst()` and E021's `persistence()`, imported unchanged.

## Gate
The pooled anchors BIBLE_EU (DEV) must have:
- mean I_word inside E019's word-family range, 0.271–0.712;
- mean PERS_30 inside E021's, 0.229–0.562.

Otherwise the verdict is VOID. The calibration gave 0.452 and 0.360: PASS.

## Decision (DEV primary; Currier B reported)
- **SIMPLE** = the 5 simple-syllable texts pooled (50 samples).
- **CONSISTENT** iff |z| ≤ 3 on all four features, with an sd floor of 0.01.
  - CONSISTENT → **RUNG 1 CONSISTENT AT WORD LEVEL**.
  - Otherwise → **RUNG 1 INCONSISTENT AT WORD LEVEL**, reported with the failing features.
- Also reported: per-text z, BIBLE_EU z, and Currier B.

## What each outcome means
- **CONSISTENT:** rung 1 (a simple-syllable language, written plainly with some glyph groups as units) explains
  every fact measured so far, apart from F5 (lines), which Bibles cannot test. It is then the simplest standing
  hypothesis. The next step is a test that could *refute* it, using a fact we have not yet looked at.
- **INCONSISTENT:** the plain version fails at the word level. The failing feature names exactly what extra part
  (if any) is forced. Following the Occam rule, we add only that part.
