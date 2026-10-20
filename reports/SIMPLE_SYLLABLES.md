# E027: Voynich against languages with simple syllables (Occam rung 0/1)

Pre-registration: `reports/E027_PREREG.md` (sha256 `93b2af885584f204d44ebaa493f18ec242142239067e6da0572eaa1451d12d72`,
locked before the run). Script: `experiments/e027_simple_syllables.py`. Results: `experiments/results/e027.json`,
`e027_run.log`.

## Verdict: **RUNG 1 NOT EXCLUDED**
When glyph groups are read as single units (E024's S2/S3: *ch*, *sh*, *aiin*, *ee*, *qo*, *dy*…), Voynich's
predictability, alphabet entropy and word length all lie inside the range of plainly written languages with rigid
syllables. The fact that sent us to ciphers (E024: "no grouping is alphabet-like") held only against European-type
languages.

| | h1 | h2 | L (units per word) |
|---|---|---|---|
| 34 E024 languages (complex syllables) | 3.53–4.53 | 2.79–3.64 | 1.30–6.80 |
| **Simple-syllable group** (Hawaiian, Tongan, Māori, Vietnamese, Mandarin pinyin; 2 renderings each) | 3.33–4.71 | **2.23–2.88** | 2.74–4.21 |
| Voynich S0 (single EVA letters) | 3.87 | 2.10 ✗ | 4.99 ✗ |
| Voynich S1 (+ benches and gallows) | 3.86 | 2.22 ✗ | 4.46 ✗ |
| **Voynich S2** (+ i-runs, e-runs) | 3.91 ✓ | 2.37 ✓ | 4.03 ✓ |
| **Voynich S3** (+ qo, dy) | 4.02 ✓ | 2.48 ✓ | 3.69 ✓ |

- **Gate passed:** the Latin Vulgate and the English KJV, the same genre as the comparison Bibles, lie inside the
  34-language range.
- **Nearest text** (in SD units) for every segmentation: **Mandarin pinyin**, distance 2.2–2.3 at S2/S3. Then Māori
  and Vietnamese.
- **Strict secondary check** (each statistic within 0.25 SD, a tolerance where only 0.9% of language pairs match):
  no single text matches. Voynich is inside the *family*, not a copy of any one sampled language.
- Rung 0 (one EVA letter per sound) stays out: raw EVA is more predictable, with longer words, than every language
  tested.

(The log line labelled "SD34" prints the 33-language SD, Telugu excluded, as pre-registered. The label is cosmetic.)

## What this does and does not mean
- **It does mean:** the simplest hypothesis with a reading still standing is *a natural language with rigid,
  simple syllables, written in its own script, where some sounds are written with fixed glyph groups*. No key and
  no cipher layer is needed to explain F1/F6. By the Occam rule, rung 3 (ciphers and codes) is no longer forced by
  anything we have measured.
- **It does not mean** Voynich is a language. Meaningless text (rung 2) could also sit inside this range. As
  pre-registered, the next step is a no-key test that separates rung 1 from rung 2.
- It is consistent with an old proposal (Stolfi's "Chinese-like" word structure): the nearest texts are
  monosyllabic, with a fixed syllable shape. That is a pointer, not a finding.
