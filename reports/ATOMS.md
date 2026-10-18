# E024 (methodology A3): what are Voynich's real letters? — no segmentation is alphabet-like

Pre-registered: reports/E024_PREREG.md (sha256 53a37b5d…). Script: experiments/e024_atoms.py.
Results: experiments/results/e024.json.

| Segmentation | units K | h1 (bits) | h2 (bits) | word length | alphabet-like |
|---|---|---|---|---|---|
| S0 raw EVA | 19 | 3.87 | **2.10** | 4.99 | no (h2) |
| S1 + ch sh cth ckh cph cfh | 25 | 3.86 | **2.22** | 4.46 | no (h2) |
| S2 + i-runs, e-runs | 32 | 3.91 | **2.37** | 4.03 | no (h2) |
| S3 + qo dy | 34 | 4.02 | **2.48** | 3.69 | no (h2) |
| 34 reference languages | | 3.53–4.53 | **2.79–3.64** | (see note) | |

**Verdict: NONE.** Under every grouping, Voynich's next "letter" is far more predictable than in any of the 34
languages. Its highest h2 (2.48, S3) is below the lowest real one: 2.79, set by Telugu, whose figure is distorted (see
note); the lowest valid language is Tagalog at 2.88. Merging glyphs raises h2 only slowly (0.13 bits per step).

Pre-registered consequence: a simple one-unit-per-letter alphabet over a real language is unlikely under these
groupings. B2 (invented alphabet) is deprioritised; the word-code and compound families from E019–E021 come
first. This replicates the published finding (Bennett; Lindemann & Bowern 2020) with our corpus.

Note (defect, not affecting the verdict): the letters-only tokenizer splits Telugu at its vowel signs (combining
marks), so Telugu's word length (1.30) and h2 are wrong. Excluding it can only raise the reference minimum, so
the verdict stands. Two languages had fewer than 28,841 words and were skipped (34, not 36).
