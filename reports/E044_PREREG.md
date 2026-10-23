# E044 pre-registration: are Voynich's spaces between syllables rather than words?

Written 2026-10-23, before the run. Script: `experiments/e044_syllable_spacing.py`.

## Question
E043 (C21): Voynich doesn't avoid putting a token right next to an identical one (AS ≈ 1), whereas every ordinary
word-spaced text does. One simple explanation is that **Voynich's spaces separate syllables, not words**, as in
written Vietnamese or Chinese, where identical neighbouring syllables are common.
- This would fit E027/E040: simple-syllable statistics, with Mandarin pinyin the nearest text.
- It would clash with E028: Voynich has far more distinct units than syllable texts (Mandarin 866, Vietnamese
  1,817 types per 28,800 tokens, against Voynich's 6,077).

The test checks both at once.

## Structural sub-hypothesis (new, set now)
| Hypothesis | Meaning | Prior |
|---|---|---|
| WORD-UNIT | Voynich's spaces separate words | 0.8 |
| SYLL-UNIT | spaces separate syllables (or similar sub-word units) | 0.2 |

The prior is low for SYLL-UNIT because of E028's vocabulary result.

## Texts
- **Syllable-spaced:**
  - Vietnamese Bible (vie1934);
  - Chinese Bible (cmn-cu89s) as characters (each character one token);
  - the same Bible as toned pinyin syllables.
- **Word-spaced controls:** Latin (Vulgate) and Indonesian.

## Design
- **Targets:** Voynich **Currier A** and **Currier B** separately, in raw EVA as in E043. DEV is not used, because
  pooling A and B inflates it (E043).
  - B is measured as the mean of 10 runs of consecutive lines at A's token count.
- **Text preparation:** each text is cut into pseudo-lines using Voynich's line-length sequence, in windows of
  8,806 tokens (up to 10, seed 44044).
- **Statistics:** SL, AS (E043 code), and types (distinct units per window).
- **Scoring:** z = (V − mean) ÷ max(window sd, 2%|V|, 0.01). A text **FITS** a target if |z| ≤ 3 on all of SL, AS
  and types.

| Outcome | Rule | Factor |
|---|---|---|
| SYLLABLE SPACING FITS | some syllable-spaced text fits A or B | SYLL-UNIT × 3 |
| SYLLABLE TEXTS AVOID ADJACENCY TOO | no syllable-spaced text has \|z(AS)\| ≤ 3 for A or B | SYLL-UNIT × 1/3 |
| PARTIAL | otherwise (AS fits, but SL or types do not) | none |

## What was seen before writing this (disclosed)
- E028's type counts for Vietnamese and Mandarin at 28,841 tokens.
- E043's results.
- A tokenisation check that printed 10–15 tokens of Vietnamese and pinyin.
- No statistic here has been computed on any syllable-spaced text.
