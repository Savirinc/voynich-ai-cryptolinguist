# E037 pre-registration (attack step 1): the grammatical shape of Voynich, key-free

Written 2026-10-21, before the run. Script: `experiments/e037_grammar_profile.py`.

## Status
From here the working assumption is **L: a real language in its own script** (ledger 0.61–0.97, see
`LEDGER.md`). Attack plan step 1: recover the shape of the grammar without reading anything.

**This is a measurement, not a ledger test.** It adds measured facts and moves no ledger probability. Its results
fix the criteria for step 2, the shortlist of candidate languages. The interpretation of each outcome is fixed here,
in advance.

## Texts
- **Voynich DEV:** all, Currier A, Currier B. Pairs are counted within lines; uncertain tokens are dropped, as in
  E031.
- **References:** the first E033 window (28,841 words) of each of these, chosen to cover the main grammar types:
  - Indonesian: doubles words, few suffixes;
  - Malay: its relative;
  - Latin: inflecting, with stem classes;
  - Swahili: agglutinative.
- LOCKED_TEST is excluded.

## Segmentation
E026's stem + ending segmenter, settings unchanged (`SEG`), seed 37037, run on each text's word types. The
references are segmented in their own letters. The comparisons are about *structure*, so the letters don't need to
be alike.

## Measurements
| Code | Question | Measure |
|---|---|---|
| G1a | How many endings? | NSUF95 (E026) |
| G1b | How many endings does a stem take? | Mean distinct endings per stem, for stems with ≥ 10 tokens |
| G1c | Does the stem decide its ending set (stem classes, as in Latin)? | I_EXCESS = [I(ending; stem) − mean I with endings shuffled across tokens, 5×] ÷ H(ending), over tokens whose stem has ≥ 5 tokens |
| G2a | Are rare or frequent words doubled? | DBL_RHO: Spearman ρ between log count and doubling rate, over types with ≥ 5 tokens |
| G2b | Are doubled words suffixed? | DBL_SUFFIXED: share of doubled pairs with an ending ÷ share of all tokens with one |
| G2c | Voynich only: are doubles placed at line starts? | DBL_LINE_FIRST: doubling rate in a line's first pair ÷ in its other pairs |
| G3a | Where do neighbouring near-copies differ? | ENDZ: share of adjacent edit-distance-1 pairs whose difference is in the last 2 units of the longer word ÷ the same share after shuffling (5×, line lengths kept). For an inserted or deleted repeated glyph (e.g. *daiin/dain*), the position is the first mismatch from the left. |
| G3b | Are near-copies the same stem with a different ending? | SAMESTEM: share with the same segmenter stem ÷ the same share after shuffling |

Also reported, descriptively, for Voynich: the top doubled words, the top 12 glyph edits in adjacent near-copies,
and the top endings.

## Interpretation, fixed in advance
| Result | Reading |
|---|---|
| G3a ENDZ ≥ 1.3 **and** G3b SAMESTEM ≥ 1.3 | Neighbouring near-copies are **forms of the same stem with different endings**: a grammar habit (agreement, repeated inflection or paradigm lists), not loose spelling. Counts against E036's "variation anywhere" picture. |
| G3a ENDZ 0.8–1.25 | Near-copies differ at no special place. Consistent with **spelling variation** (E035/E036). |
| G3a ENDZ < 0.8 | They differ inside words: variation in the stem, or in the script's glyph clusters. |
| G2a DBL_RHO < −0.1 | Rarer, content-like words are the ones doubled, **as in Indonesian reduplication**. The Indonesian reference value is the yardstick. |
| G2a DBL_RHO > +0.1 | Frequent words are the ones doubled: function words, fillers or drill items, **not** like Indonesian. |
| G2c DBL_LINE_FIRST ≥ 2 or ≤ 0.5 | Doubling is tied to line position, a writing convention, and less likely grammar. |
| G1c I_EXCESS | Reported with the nearest reference. High (Latin-like) means stems belong to classes. Low means endings attach freely (agglutinative-like). |
| Currier A vs B | Any measure that differs by more than a factor 1.5 between A and B is reported as an A/B grammar difference. |

**What would change the plan.** If near-copies turn out to be inflected forms (row 1), step 2's shortlist must
require **inflection**, and the E035/E036 spelling-variation picture is down-weighted in prose (not in the
ledger). Otherwise, the shortlist criteria are:
- simple syllables;
- doubling of the measured kind;
- the measured ending system.

## What was seen before writing this (disclosed)
- E026's endings and PAR.
- E030–E036's R and NR.
- Well-known doubled Voynich words from the literature (e.g. *qokedy qokedy*, *daiin daiin*).
- The helper functions were checked on toy words. No measure here has been computed on any text.
