# E056 pre-registration: are the zodiac nymph labels numbers?

Written 2026-10-24, before the run. Script: `experiments/e056_zodiac_numbers.py`.

## Question
The owner asked whether the common words used as labels could be **numbers**. The zodiac pages are the clearest place
to look: each sign has about 30 small figures (like the days of a month or the degrees of a sign), each with a label,
arranged in rings.
- If the labels count the figures, or give their degree, then **the same ring position on different months should
  carry the same word**;
- and the labels should come from a **small closed set** of number-words.

## Sub-hypothesis (new, set now)
**NUMBERS:** the zodiac nymph labels are numbers or degrees in ring order. Prior **0.2**; the alternative (names or
other words) is 0.8.
- **Why this prior.** E051 already found that only 29% of labels recur on another zodiac page, which argues against a
  simple count. The owner's idea and the labels' generic use across sections argue for keeping it open.

## Data
- **Pages:** the 12 DEV zodiac pages, f70v1–f73v (none is locked).
- **Labels:** mode 'label', one per transcription line, in ring order as transcribed. The first word of each label is
  used, since some labels have two or three words.

## Statistics
- **A. Positional alignment:** over all pairs of pages, and positions k = 1 to min(n_i, n_j), the share of positions
  where the two labels are identical. The null shuffles labels within each page (10,000 permutations, seed 56056).
  The p-value is one-sided.
- **B. Closed set:** the type/token ratio, and the number of label types needed to cover 80% of label tokens.

## Controls
- **Positive (planted numbers):**
  - **What is planted:** the same page sizes, but labels replaced by 30 "number words" (30 distinct real Voynich label
    words, drawn at random) by position.
  - **Noise added:** 12% of labels get one random glyph change, and 20% are replaced by a random other label word.
  - **Required:** p < 0.01 and type/token < 0.5, otherwise the test is VOID.
- **Negative:** the real labels shuffled across all pages (reported).

## Decision
| Outcome | Rule | Factor |
|---|---|---|
| VOID | the positive control is not detected | none |
| LABELS ALIGN BY POSITION (number-like) | Voynich p < 0.01 | NUMBERS × 10 |
| NOT NUMBERS | p ≥ 0.2 **and** type/token > 0.6 | NUMBERS × 1/10 |
| INCONCLUSIVE | otherwise | none |

## Limits (stated now)
- **The transcription's ring order** might start at different points on different pages. A rotated numbering would
  then be missed. Only same-start numbering is tested here.
- **Aries and Taurus are each split over two pages** (about 15 figures each), so their numbering might continue across
  pages. Not modelled.
- **A NOT NUMBERS result therefore excludes** only "numbers in the same order from the same starting point".

## What was seen before writing this (disclosed)
- E051's cross-page repeat rate (29%) and type count (277 types in 341 label tokens).
- The label lines of f71v.
- No alignment statistic has been computed.
