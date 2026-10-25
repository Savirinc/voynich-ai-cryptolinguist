# E065: the syllable route, go/no-go — NO GO

Pre-registration `reports/E065_PREREG.md` (sha256 887fbb75…ac0774), script `experiments/e065_syllable_gonogo.py` (sha256
cef4c3da…34d1e3), locked in the commit before the run. Results `experiments/results/e065.json`, `e065_run.log`. 16 s.

## Verdict: NO GO on both halves. Absence rule on the syllable form: L × 0.921.

**Plain reading.** Voynich words end in very few distinct glyph groups: 25 classes cover 95% of all words (y, none, dy,
ol, aiin, or, ar, ain, al, ey, edy, o…). If each Voynich word were a real word written syllable by syllable, those 25
classes would have to carry the language's final syllables. No European-region language comes close: their words end
in 284–481 distinct syllables (95% coverage), and 68–154 even when the closing consonant is dropped as Linear B does.
The nearest, Turkish with codas dropped (68), is still above the bar of 50 by a clear margin. The second idea, that each
Voynich word is a single syllable of a European text, fails harder: syllable streams have 826–1,499 distinct types per
28,841 against Voynich's 6,077, and 18–31% one-offs against 68%.

## Half 1: final-syllable inventories
Bar: F95 ≤ 2 × E95 = 50 (Voynich E95 = 25; the last S3 unit alone gives 8 classes).

| Language | Syllables per word (typical) | Final syllables, FULL (F95) | Final syllables, codas dropped (CV F95) | All syllables S95 (FULL / CV) | Pass? |
|---|---|---|---|---|---|
| Turkish | 2.63 (2.5) | 284 | **68** | 395 / 78 | no |
| Hungarian | 2.12 (2.3) | 481 | 79 | 641 / 90 | no |
| German | 1.50 (1.8) | 437 | 92 | 709 / 131 | no |
| Dutch | 1.44 (1.7) | 377 | 112 | 608 / 149 | no |
| Czech | 1.86 (2.0) | 412 | 122 | 611 / 153 | no |
| Latin | 2.07 (2.4) | 424 | 123 | 591 / 143 | no |
| French | 1.54 (1.7) | 377 | 132 | 617 / 159 | no |
| Polish | 1.88 (2.1) | 438 | 136 | 764 / 177 | no |
| English | 1.37 (1.4) | 441 | 136 | 663 / 170 | no |
| Italian | 1.87 (2.3) | 122 | 86 | 341 / 111 | UNRELIABLE (gate), would fail |
| Greek | 2.02 (2.5) | 354 | 154 | 573 / 200 | UNRELIABLE (gate), would fail |

The syllabifier undercounts syllables (it treats every vowel run as one nucleus, so *dei-nen* but also *e-gre-dien-tur*),
which put Italian and Greek outside the ±0.4 gate. Undercounting *merges* syllables and so *lowers* F95; the real
inventories are larger. Both unreliable languages fail by a wide margin anyway, and they are counted as untested.

## Half 2: each Voynich word as one syllable
Bar: 4,860–7,290 distinct types and ≥ 55% one-offs (Voynich 6,077 and 68%).

| Stream | Types | One-offs | Zipf | R | NR |
|---|---|---|---|---|---|
| Voynich words | 6,077 | 0.68 | −0.65 | 2.65 | 2.10 |
| Polish syllables | 1,499 | 0.27 | −0.64 | 0.21 | 0.91 |
| German syllables | 1,482 | 0.31 | −0.62 | 0.33 | 0.64 |
| English syllables | 1,422 | 0.27 | −0.79 | 0.03 | 0.58 |
| Latin syllables | 1,246 | 0.26 | −0.53 | 0.38 | 0.94 |
| Turkish syllables | 879 | 0.18 | −0.65 | 0.66 | 1.35 |
| Italian syllables | 826 | 0.22 | −0.72 | 0.22 | 0.96 |
| Vietnamese words (real syllable text, reference) | 1,500 | 0.24 | | 0.27 | 1.10 |

A syllable stream has a small, closed inventory with few one-offs, the opposite of Voynich's word list. Vietnamese, a
language actually written one syllable per word, behaves exactly like the artificial streams. pfeaster's hypothesis
fails the go/no-go he himself named, by a factor of four in vocabulary.

## Ledger
NO GO with 9 of 11 reliable: coverage 0.6 × 9/11 = 0.49; L-syll share 0.20; m 0.2 → **L × 0.921**.

| | M | L | C | O |
|---|---|---|---|---|
| Before (after E064) | 0.024 | 0.9445 | 0.0274 | 0.004 |
| **After E065** | **0.0259** | **0.9401** | **0.0296** | **0.0043** |

Sensitivity: from the range edges (M 0.25, L 0.60 × 1/3 after E064, C 0.13, O 0.02) L × 0.921 gives M 0.43, L 0.31,
C 0.22, O 0.03; the E064 picture (M leads from the edges) is unchanged.

**Forms of L after E065** (shares of L): lost or unrecorded language **0.33**, syllable signs 0.20, abbreviation 0.18,
mixed or other 0.16, letter by letter 0.14. The lead within L has passed to the one form no dictionary can search.

## What this does not cover
- Syllabaries of Hebrew, Arabic or languages not on disk (the 0.4 of the form left uncovered).
- A many-to-one system merging far more than codas (an "alphabet of 25 endings" would be a cipher-like code, under C).
- The crude syllabifier: its errors make inventories smaller, not larger, so they favour the hypothesis that failed.
