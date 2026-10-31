# E110 pre-registration: are p and f two forms of one letter, or different (possibly opposite) letters? (Arham, 2026-10-31)

## Question
Arham listed every word pair that is identical except for *p* ↔ *f* (113 pairs, `reports/data/pf_pairs.csv`). If *p* and
*f* are different letters (perhaps opposites), the choice between them should depend on **which word** it is. If they
are two pen forms of one letter, the choice should depend only on context (scribe, paragraph position, slot in the
word) and be the same for every word.

## Data and procedure (`experiments/e110_pf_same_or_different.py`)
- **Frames:** DEV pages only (LOCKED_TEST excluded). A frame is a pair of words identical except *p* ↔ *f*, where each
  word contains exactly one *p* or *f*.
- **Witnesses set aside:** each frame exists only because both versions occur, so one *p*-token and one *f*-token per
  frame are set aside at random. The test uses the remaining 484 tokens in 83 frames.
- **Strata:** scribe × paragraph-first line × slot of the letter (first letter; after a prefix *o/qo/y/l/ch/sh/ol*;
  inside a *c?h* bench; other).
- **Statistic:** G = the sum over strata of the likelihood-ratio statistic of the frame × letter table.
- **Null:** letters permuted within strata, 5,000 times.
- **Known answers** (Latin latVUC, Italian ita1885; strata: line-first × letter is word-initial):
  - **CONTRASTIVE:** the consonant pair with the most minimal-pair frames, chosen by rule among b/p, d/t, c/g, f/v, m/n,
    r/l, s/t (it is *s/t* in both languages). Over 20 size-matched subsamples it must give p < 0.01 in ≥ 80%.
  - **ALLOGRAPH:** *t* is given a random second form *T* (probability 0.3 at word start, 0.1 elsewhere). It must give
    p < 0.01 in ≤ 10%.
- **Validity:** both conditions hold in both languages.

| Outcome | Rule |
|---|---|
| WORD-SPECIFIC (they act as different letters) | p < 0.01 |
| WEAK | 0.01 ≤ p < 0.05 |
| SAME-LETTER-LIKE (two forms of one letter) | p ≥ 0.05 |
| VOID | validity fails |

- **Rule 8:** if 0.005 ≤ p ≤ 0.02 or 0.035 ≤ p ≤ 0.07, run 10 fresh permutation seeds; at least 8 must agree,
  otherwise WEAK.
- **No Bayes factor.** This is about the script's letters.
- **Unscored:** the frames with the strongest own preference, and co-location (pages where a word's *f*-version shares
  the page with its *p*-version).

## Calibration done before locking (known answers only; no Voynich statistic computed)
1. **Labels assigned inconsistently.** The first version let a word with the letter in two places belong to two
   frames, which gave inconsistent labels. Planted allographs were then flagged as word-specific (Italian 9/20,
   Latin 3/20). Fixed by keeping only words with exactly one *p*/*f*.
2. **Conditioning on both versions existing.** Requiring both versions to exist biased rare frames towards balance, so
   Latin allographs were still flagged 5/20. Fixed by setting aside one token of each version per frame.
3. **After both fixes,** 20 size-matched runs (500 permutations) gave:

   | Language | Allograph false alarms | Contrastive caught | Median p (allograph / contrastive) |
   |---|---|---|---|
   | Italian | 0/20 | 18/20 | 0.34 / 0.002 |
   | Latin | 0/20 | 19/20 | 0.18 / 0.002 |

## Seen beforehand
- The pair list with counts by scribe, section and paragraph line. *p*:*f* is about 2.6 : 1 overall, ranges 1.2–3.6 by
  scribe, and only a few frames lean towards *f*. This descriptive impression suggested "same letter"; it is disclosed
  here.
- E109 (*f*/*p* in opposite halves of rings, WEAK) and X109 (f57v).
