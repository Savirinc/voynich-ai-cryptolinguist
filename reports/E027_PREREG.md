# E027 pre-registration: Occam rung 0/1, against languages with simple syllables

Written 2026-10-20, before the run. Script: `experiments/e027_simple_syllables.py`. See `reports/OCCAM.md` for why.

## Question
E024 ruled out a plain alphabet because Voynich's glyphs are more predictable (h2 2.10–2.48) than any of our 34
reference languages (≥ 2.79). All 34 have complex syllables. Is Voynich inside the range of natural languages with
**rigid, simple syllables**, written plainly? If it is, the main reason we climbed to ciphers and codes (rung 3)
disappears.

## What was already known when this was written (no blind test)
- Voynich's E024 values for every segmentation S0–S3 were already published in `reports/ATOMS.md`.
- The no-Voynich calibration run (`--calib`, `experiments/results/smoke/e027_calib.json`) was done first. It showed
  the comparison texts' values. Those values were seen before this was written.

Because both were known, **no rule is chosen here**. The primary rule is E024's rule, copied unchanged and applied to
a new comparison group. The secondary tolerance is fixed by a base-rate rule that uses only the reference languages.

## Data
- Voynich DEV prose words (28,841), from `E.voynich_lines()`. The LOCKED_TEST leaves are excluded.
- Comparison texts: eBible.org Bibles, downloaded 2026-10-20. They are not redistributed; Māori 2012 is
  copyrighted. One genre, so genre cannot differ between languages. Each sample is 28,841 words, after skipping the
  first 2,000.

| Text | Role | sha256 of the downloaded zip |
|---|---|---|
| haw1868 Hawaiian | simple | `5453826aa200fce4c0d27c249da9fd8bf16191d01849060eda1c0c787389d8c6` |
| ton Tongan | simple | `aca2d4c72ece5bf436d0762b2cf73d172a6632ccce942e3bfbfcece6328d7f64` |
| mri2012 Māori | simple | `b1758f73adfc907e2ee71b8d75a358b0577f55e0b3f1f4cccb89b92150684e0a` |
| vie1934 Vietnamese | simple | `7fd630526f60a4d3325e120de8b05989b9307c42035be1d2574e3d4eda29a360` |
| cmn-cu89s Mandarin → pinyin (pypinyin 0.55.0), one word per syllable | simple | `4785e4ad40f124bbdca53b32fbcf9fb13c33432519a2289ccf7edc214381c748` |
| latVUC Latin Vulgate | genre anchor | `35654870f7391f46961aaf61b5333c39d4bacd9c38984d3b8768912fc4038e83` |
| eng-kjv English KJV | genre anchor | `74088f16b29563c30e16ee6eacf95b33689ba4bbd6dea15179fe46b83dc86a51` |

Japanese was dropped before the calibration run. Automatic word splitting of Japanese gives wrong words (pykakasi
"gaatta"), and adding a segmenter would be an extra moving part.

Two renderings per text:
- **NATIVE**: Unicode NFC, with pinyin toneless.
- **MARKS**: NFD, with combining marks as separate units and pinyin's tone digit as a final unit.

## Procedure
- **Statistics:** E024's `metrics` (h1, h2, L) on each text and on Voynich under E024's segmentations S0–S3.
- **Also reported, not decisive:** E026's ending features, with the same segmenter settings and seed 27027.
- **Gate:** the Vulgate and the KJV (NATIVE) must lie inside the E024 34-language range on h1, h2 and L. Otherwise
  the verdict is VOID. The calibration run passed this gate.

## Decision
- **Primary (E024's rule):** Voynich segmentation S is INSIDE iff each of h1, h2 and L lies in [min, max] of the
  simple-syllable group, which is 5 languages × 2 renderings.
  - S0 INSIDE → **RUNG 0 NOT EXCLUDED** (a plain script, one glyph per sound).
  - Else any of S1–S3 INSIDE → **RUNG 1 NOT EXCLUDED** (some sounds written as fixed glyph groups).
  - Else → **RUNGS 0–1 OUT**.
- **Secondary (strict, reported):** MATCH(text, S) iff |difference| ≤ c·SD33 on each of h1, h2 and L. SD33 is the
  between-language SD of the 33 E024 references, excluding Telugu, as E024 flagged. c is the largest of 0.25, 0.5,
  0.75 and 1.0 whose pair base rate among the 33 languages is ≤ 0.05. The calibration gives c = 0.25, with a base
  rate of 0.009.

## What each outcome means, written in advance
- **NOT EXCLUDED** does *not* mean Voynich is a natural language. It means the predictability fact (F1/F6) no longer
  forces a cipher or code. Meaningless text could also fall inside. The next Occam step would then be a test that
  separates rung 0/1 from rung 2 (human gibberish), with no key and no search.
- **OUT** means even simple-syllable languages are too unpredictable or have the wrong word length, so climbing the
  ladder is justified by a documented fact.
