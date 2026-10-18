# E020 (methodology A1b): drift and compound words — no family fits all four features

Pre-registered: reports/E020_PREREG.md (sha256 5fbc4212…). Script: experiments/e020_drift_compound.py.
Results: experiments/results/e020.json, e020_run.log. 40 samples per family.

Voynich DEV: I_word 0.387, top_word 0.285, I_sub 0.150, top_sub 0.582.

| Family | I_word z | top_word z | I_sub z (twin range) | top_sub z | RMS z | Consistent (all \|z\| ≤ 3) |
|---|---|---|---|---|---|---|
| Naibbe, new key per 4 sections | +3.4 | +1.9 | +12.0 (0.020–0.039) | +5.9 | 6.98 | no |
| Naibbe, new key per 8 sections | **+0.4** | **−2.7** | +11.3 (0.028–0.043) | +3.2 | 6.01 | no |
| Real words, strong spelling drift | −2.9 | −5.1 | −5.0 (0.364–0.738) | −4.3 | 4.42 | no |
| Compound (stem codeword + ending) | **−0.2** | **−2.1** | +6.4 (0.014–0.071) | +2.0 | 3.49 | no |
| Compound, ending tables by section | −1.5 | −7.9 | **+2.9** (0.049–0.123) | **+0.8** | 4.31 | no |

**Pre-registered verdict: nothing CONSISTENT.**

## What it means
1. **E019's rejection of the letter-level cipher is not robust.** A Naibbe-class cipher whose key changes every
   eighth of the book matches Voynich's word-level clustering (z +0.4, −2.7). Word-level clustering alone cannot
   separate "word-sized units" from "letter cipher with changing keys". UNIT_BURSTINESS.md is amended accordingly.
2. **The discriminating feature is clustering of glyph pairs inside words.** Voynich (0.150) is far above every
   cipher with changing keys (≤ 0.043): changing which strings stand for which letter doesn't change which glyph
   pairs get written. It is also above real words and compound words (≤ 0.12), and far below strong spelling
   drift (≥ 0.36). Voynich's glyph-level habits change along the book moderately: more than plain language, less
   than our drift setting.
3. **Closest:** compound words (fit both word-level features; glyph pairs too stable) and compound words with
   section-specific endings (glyph pairs right; too many topic-bound types). A word-or-compound system written by
   scribes whose glyph habits differ moderately is the natural next candidate. It matches the known Currier A/B and
   five-scribe evidence (Davis 2020).
4. **Still open for a cipher:** only one whose glyph inventory itself changes by section, not just its key.

## Next (methodology order)
- A1c: drift-vs-topic separation. In language, the most frequent function words persist across all sections;
  under a key change they vanish together. Measure persistence of the top types across Voynich sections and scribes,
  against the families above.
- A2: labels against pictures (meaning test).
