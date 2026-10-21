# E030 pre-registration (ledger test 1): do languages that double words match Voynich's word repeats?

Written 2026-10-21, before the run. Script: `experiments/e030_reduplication.py`. Updates `reports/LEDGER.md`.

## Question
Fact C9: Voynich puts a word next to a copy of itself 2.3× more often than chance, given its word frequencies,
while Latin prose does it at 0.02–0.28× chance. Can a real language do what Voynich does? Languages that double
words (reduplication, e.g. Malay *orang-orang* "people") are the best candidates. If even they stay below chance,
C9 counts against L, and against the word-preserving part of C.

## Data
- **Primary group (tokens are words), 10 texts:** Indonesian (indayt), Malay (zlmKSZI, New Testament only),
  Tagalog (tglulb), Cebuano (cebulb), Swahili (swhulb), Yoruba (yor), Hausa (hausa), Hawaiian (haw1868), Tongan (ton)
  and Māori (mri2012). Austronesian languages use reduplication heavily; Swahili, Yoruba and Hausa use it too.
- **Secondary (tokens are syllables, reported only):** Vietnamese (vie1934), and Mandarin as *toned* pinyin
  (cmn-cu89s). Toned pinyin is used because toneless pinyin would merge different syllables into false repeats.
- **Anchors:** Latin Vulgate (latVUC) and English KJV (eng-kjv).
- **Source:** eBible.org, downloaded 2026-10-21 (E027 Bibles from 2026-10-18). Zip sha256 values are written to the
  output.
- **Words:** lowercase letter runs. Hyphens split words, so written reduplication counts as a repeat; this is
  generous to L.
- **Sampling:** 10 random windows of 28,841 tokens (DEV size) per text, seed 29029. A text's value is the mean over
  its windows.
- **Voynich:** DEV prose, within-line pairs, clean tokens (same as E029a).

## Statistic
R = (adjacent repeats / adjacent pairs) ÷ Σ p_w², which is the observed repeat rate over the rate expected if words
were in random order. Also reported:
- the raw repeat rate;
- the near-repeat rate (neighbouring words differing by one letter).

## What was seen before writing this (disclosed)
- Voynich: R ≈ 2.3, raw 0.95%, near-repeats 3.65%.
- Four Latin Library texts: R 0.02–0.28.
- None of the new Bibles has been looked at.

## Gate
Both anchors must have R < 1.0, or the verdict is VOID. If Bibles in European languages did not avoid repeats, the
Bible genre would not be comparable.

## Decision and ledger update (fixed now)
Let Rmax be the largest R in the primary group.

| Outcome | Rule | Bayes factor |
|---|---|---|
| LANGUAGES CAN DO IT | Rmax ≥ 1.5 | L × 3 |
| NEUTRAL | 1.0 ≤ Rmax < 1.5 | none |
| NO LANGUAGE ATTRACTS REPEATS | Rmax < 1.0 | L × 1/10, C × 1/3 |

**Why the factors are asymmetric.** The starting ledger already discounted L a little for C9, so finding a
language that does it only removes that discount (×3). If no language that doubles words even reaches chance,
Voynich's 2.3× becomes something real languages do not do, which is a moderate factor against L (×1/10). C × 1/3
because only the word-preserving part of C inherits the language's repeats. M and O are unchanged before
renormalising.

## Limits (stated in advance)
- Bibles are translations, and translators may avoid colloquial reduplication.
- Voynich pairs are counted within lines, while Bible windows run across verses. Line edges only lower Voynich's
  count.
- Only one positive outcome is tested: that a language *can* do it. The test does not show Voynich *is* one of
  these languages.
