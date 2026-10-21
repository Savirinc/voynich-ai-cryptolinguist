# E035 (ledger test 6): real languages with free spelling variation — VARIATION MATCHES (narrowly)

Pre-registration: `reports/E035_PREREG.md` (sha256 6ae85f58…1ce3, locked before the run, commit 6f4ae11). Script
`experiments/e035_spelling_variation.py`. Results: `experiments/results/e035.json`, `e035_run.log`.

## Plain-language result
**Indonesian, with one rule added (common words get spelled several ways, at random), matches Voynich on 8 of 9 word
features.** Only one parameter was tuned, and only to get the number of distinct words right. The other matches were
predictions, including the two facts no text had matched before:
- **the flat Zipf head:** −0.68 against Voynich's −0.65, where every plain text was −0.79 or steeper;
- **the near-copies:** NR 2.11 against Voynich's 2.14.

The one clear failure is **words seen only once**: 58% against Voynich's 68%. By the pre-registered rule (best text
fails at most 1 of 9): **VARIATION MATCHES**, so L × 10 and C × 3.

| Feature | Voynich | Indonesian + variation (α = 1.5) | z | Plain Indonesian (E033) |
|---|---|---|---|---|
| distinct words (fitted) | 6,077 | 6,135 | −0.1 | 3,049 |
| exact neighbour copies, R | 2.65 | 2.73 | −0.1 | 2.76 |
| near-copies, NR | 2.14 | 2.11 | +0.0 | (not scored) |
| Zipf slope, top 100 | −0.65 | −0.68 | +0.8 | −0.85 (fail) |
| topic clustering, I_word | 0.39 | 0.30 | +1.0 | |
| topic clustering, top_word | 0.29 | 0.25 | +0.5 | |
| persistence, PERS_30 | 0.26 | 0.49 | **−2.98** (just inside) | |
| persistence, COV_30 | 0.92 | 0.97 | −2.75 | |
| words seen once | 0.68 | 0.58 | **+6.0 (fail)** | 0.53 (fail) |

## Read this carefully
- **The match is narrow.**
  - Persistence passes by a hair (z −2.98 against a limit of 3), and COV_30 is close (−2.75).
  - With a slightly different seed, Indonesian could fail 2 or 3, which would be PARTIAL or NO MATCH. The rule was
    fixed in advance and is applied as written. The margin is stated here so nobody over-reads it.
- **Only one text matched.**
  - Malay, the closest relative of Indonesian, fails 4 (persistence, COV_30, hapax, NR 1.2).
  - Languages that don't double words fail R badly, as predicted in advance: variation cannot create repeats.
- **What it shows:** one mechanism is enough to produce Voynich's whole word-level profile, starting from a real
  language. That mechanism is a language that doubles words, with common words spelled several ways. That had not
  been shown before; until now no text and no generator came within 2 features.
- **What it does not show:**
  - It does not show that Voynich *is* Indonesian-like, or that this is what happened.
  - It does not show what the text says.
  - A glyph-level homophone cipher would produce the same effect, which is why C also gets a smaller factor.
- **The remaining miss:** Voynich has more one-off words than this model makes, and it persists less. Both point
  the same way: Voynich's variation is *more scattered* than "pick from the spellings already used". Spellings may
  be invented more freely, or long words may vary more.

## Ledger
L × 10 and C × 3, as pre-registered. The new values are **M 0.006, L 0.970, C 0.023, O 0.001**. See `LEDGER.md` for
the fragility notes, which still apply.
