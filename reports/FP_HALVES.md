# E109 (Arham): do f and p sit in opposite halves of rings elsewhere in the book?

- **Pre-registration:** `E109_PREREG.md`.
- **Script:** `experiments/e109_fp_halves.py`. Rule 8 check: `e109b_seed_check.py`.
- **Results:** `experiments/results/e109.json`, `e109b.json`, log `e109_run.log`.

## Verdict (pre-registered): WEAK, no factor
Seven rings outside f57v contain both *f* and *p*. They are on f70r1, f70r2, f72v1 and f73v (zodiac), f85r2
(cosmological) and two on the Rosettes. In these rings *f* and *p* sit in opposite halves of the circle more than
random placement gives: TOTAL 6.47, p 0.041.

| Ring | f, p | Separation (1 = perfect) |
|---|---|---|
| f70r1, ring 3 | 1, 1 | 1.00 |
| f70r2, ring 17 | 1, 2 | 1.00 |
| f72v1, ring 22 | 3, 6 | 0.67 |
| f73v, ring 5 | 1, 5 | 0.80 |
| f85r2, ring 1 | 1, 6 | 1.00 |
| Rosettes, ring 87 | 2, 1 | 1.00 |
| Rosettes, ring 94 | 1, 3 | 1.00 |

- **Validity:** VALID. A planted perfect split was caught in 99.5% of replicates; random placement gave a false alarm
  1.5% of the time; an 80% split was caught only 10% of the time.
- **Rule 8:** p was near the 0.05 boundary, so a seed check (E109b, 10 seeds × 10,000 permutations) was run. It gave
  p 0.039–0.046, 10 of 10 below 0.05, so WEAK is stable.
- **Process slip:** the rule-8 clause was again missing from the pre-registration. This is the third time (E106, E108,
  E109). Future pre-registrations will include it.

## Caveats
- **Very little data:** 7 rings and 10 *f* in all. A ring with one *f* and one *p* is always "perfectly split", which the
  permutation null takes into account.
- **No common direction.** In reading order *p* comes after *f* in 4 rings and before it in 3. On f57v, *f* came
  first. The separation looks real; a fixed order across the book is not shown.
- The rings come from just three kinds of page (zodiac, cosmological, Rosettes).

## What it means
There is weak support for Arham's idea. Where a circle holds both *f* and *p*, they tend to keep to opposite sides of it,
as on f57v. That fits *f* and *p* marking two halves or two opposite states of a cycle, but the evidence is thin. A
larger test would need more data: radial texts, labels around circles, or the image positions of *f* and *p* on the
diagrams.

## Ledger
No change: M 0.7422, L 0.1816, C 0.0342, O 0.0421.
