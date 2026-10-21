# E030 (ledger test 1): languages that double words — LANGUAGES CAN DO IT

Pre-registration: `reports/E030_PREREG.md` (sha256 27d929fd…e86d, locked before the run). Script
`experiments/e030_reduplication.py`. Result: `experiments/results/e030.json`.

## Plain-language result
Indonesian and Malay put a word next to a copy of itself **as often as Voynich does, or more**: Indonesian 3.0×
chance and Malay 1.7×, against Voynich's 2.65×. The reason is grammar. These languages make plurals and many other
forms by doubling a word: *orang-orang* "people", *anak-anak* "children", *laki-laki* "man", *masing-masing*
"each". European Bibles stay far below chance (Latin 0.04×, English 0.01×), as Latin prose did in E029a.

So "real languages never do this" is false. Voynich's word-repeat habit (C9) does not count against a real language
after all, provided it is one that doubles words. The pre-registered update applies: **L × 3**.

## Numbers (R = repeat rate ÷ chance; mean of 10 DEV-sized windows)
| Text | R | range | raw repeats | near-repeats |
|---|---|---|---|---|
| **Voynich DEV** | **2.65** | — | 0.95% | 3.64% |
| Indonesian (indayt) | **3.03** | 1.97–3.89 | 2.40% | 0.10% |
| Malay (zlmKSZI, NT) | **1.71** | 1.53–1.96 | 1.21% | 0.12% |
| Yoruba | 0.53 | 0.29–0.84 | 0.51% | 3.93% |
| Hausa | 0.27 | | 0.31% | 3.91% |
| Tongan | 0.27 | | 0.46% | 6.65% |
| Hawaiian | 0.25 | | 0.57% | 6.61% |
| Swahili | 0.21 | | 0.20% | 0.49% |
| Tagalog | 0.04 | | 0.08% | 0.56% |
| Cebuano | 0.02 | | 0.05% | 0.78% |
| Māori | 0.02 | | 0.04% | 3.03% |
| *Vietnamese (syllables)* | 0.38 | | 0.24% | 1.12% |
| *Mandarin, toned pinyin (syllables)* | 0.35 | | 0.34% | 1.28% |
| Anchor: Latin Vulgate | 0.04 | | 0.04% | 0.39% |
| Anchor: English KJV | 0.01 | | 0.02% | 0.72% |

Gate passed (both anchors < 1). Primary max R = 3.03 (Indonesian) ≥ 1.5, so the verdict is **LANGUAGES CAN DO IT**.

## What it means, and what it does not
- In Indonesian the repeats are real grammar, spread over 973 different words, not a few odd ones. Voynich's
  repeats are spread the same way, over 97 word types in a DEV-sized sample.
- Most languages that double words, Tagalog and Swahili for example, do **not** reach chance in written Bibles.
  Doubling in Tagalog is often of a syllable *inside* a word. So this is a property of some languages and some
  spelling conventions, not of "languages with reduplication" in general.
- **Generous assumption:** Indonesian writes doubled words with a hyphen, and we counted that as two words. If the
  Voynich writer wrote a doubled word as two words, the comparison is fair.
- **Exploratory difference (not part of the rule):**
  - Voynich also has many *near*-copies (3.6%); Indonesian has almost none (0.1%).
  - Short-word languages such as Hawaiian and Tongan have even more near-copies (6.6%), so near-copies alone
    separate nothing.
  - What no language here shows is **both together**: frequent exact copies *and* frequent near-copies. That
    combination is a candidate for the next test. It is noted here, not used.
- This does not say Voynich is Malay or Indonesian. E024 (letters) already excludes those as plain alphabetic
  writing. It says the habit itself is language-like.
