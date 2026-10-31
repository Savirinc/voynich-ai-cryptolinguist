# E109 pre-registration: do f and p sit in opposite halves of rings elsewhere in the book? (Arham, 2026-10-31)

## Question
On f57v, ring 2 has *f* in the two copies of its first half and *p* in the two of its second half (X109). Arham asks
whether *f* and *p* are "opposites" that mark halves of a cycle, and whether that rule holds elsewhere. This test
asks: in the other circular texts of the book, do *f* and *p* occupy opposite halves of the ring more than chance
gives?

## Data
- ZL 3b, mode *circle*, clean tokens, DEV only (LOCKED_TEST leaves excluded), with f57v excluded because the pattern
  was found there.
- Of 76 remaining rings, only **7 contain both letters**. Their (f, p) counts are (1, 1), (1, 2), (3, 6), (1, 5),
  (1, 6), (2, 1), (1, 3). In all, *f* is scarce in ring text: 12 *f* against 62 *p* over the 76 rings.

## Procedure (`experiments/e109_fp_halves.py`)
- **Positions:** each *f* and *p* gets a position along its ring, taken as a circle, so where the transcriber started
  does not matter.
- **SPLIT** (per ring): the largest difference, over 72 cut points, between the share of its *f* inside a half-circle
  and the share of its *p* inside the same half. 1 means perfectly separated.
- **TOTAL** = the sum over the 7 rings.
- **Null:** *f*/*p* labels permuted among each ring's *f* + *p* positions, 10,000 times.
- **Known answers** (same rings and counts, synthetic positions, 200 replicates):
  - PERFECT split;
  - 80% split;
  - RANDOM.
- **Validity:** PERFECT p < 0.01 in ≥ 90% of replicates, and RANDOM p < 0.01 in ≤ 5%.

| Outcome | Rule |
|---|---|
| SPLIT ACROSS THE BOOK | p < 0.01 |
| WEAK | 0.01 ≤ p < 0.05 |
| NO SPLIT | p ≥ 0.05 |
| VOID | validity fails |

- **Power, stated in advance:** the smoke run caught a perfect split 100% of the time, an 80% split only 20%, and gave
  random false alarms 0%. NO SPLIT therefore rules out a strict rule, not a partial one.
- **No Bayes factor.** This is about a notation convention.
- **Unscored:** per-ring SPLIT, and whether *f* comes before *p* in reading order.

## Seen beforehand
- X109 (f57v): copies 1–2 have *f* and copies 3–4 have *p*, with one copy per face.
- Counts of *f* and *p* per ring, but not their positions.
- The smoke run on synthetic positions only.
