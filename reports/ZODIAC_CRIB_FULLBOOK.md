# E095b (Test B2): a zodiac crib key, proven on the whole book

Pre-registration `E095B_PREREG.md` (sha256 d44e2ad1…), script `experiments/e095b_crib_fullbook.py` (sha256 fdade7f6…).
Results `experiments/results/e095b.json`, log `e095b_run.log`. Run 2026-10-28, 62 min.

## Question (Arham)
"Even if we get one right, we can test that key properly on all the text." Does the true crib (each zodiac page's own
sign meanings) yield a letter key that reads the WHOLE book (Voynich A or B prose) better than keys built from wrong
cribs (the same meanings put on the wrong pages)?

## Method in one paragraph
- **Stage 1 (zodiac):** collect keys over the 23 VOY23 signs under which the zodiac pages contain their sign's
  meaning words. Rank them by letter-pair plausibility on the whole book and keep the top 8.
- **Stage 2 (whole book):** complete each key with the validated E047 decoder (crib letters clamped), on Voynich A or
  on B. Score it by language-model fit per sign.
- **Null:** 99 wrong cribs.
- **Scoring:** max-T over 12 configurations (6 languages × A, B).
- **Calibration first:** the true crib must beat all 99 wrong cribs (p ≤ 0.01) on synthetic books with a known key, in
  Latin, French/Occitan and Hebrew.

## Verdict: VOID (calibration failed)
| Calibration book | True crib score | Wrong-crib mean (sd) | Wrong-crib best | z | p | Needed |
|---|---|---|---|---|---|---|
| Latin | −2.197 | −4.236 (0.66) | −2.197 | +3.1 | 0.03 | ≤ 0.01 ✗ |
| French/Occitan | −2.037 | −5.094 (0.53) | −2.264 | +5.8 | 0.01 | ✓ |
| Hebrew | −2.768 | −4.514 (0.29) | −3.389 | +6.1 | 0.01 | ✓ |

**Why Latin failed:**
- Two of the 99 wrong Latin cribs ended at exactly the true crib's score. That means the whole-book decoder repaired
  those wrong keys all the way to the true key.
- On an easy synthetic book the decoder needs no crib, so a wrong crib can do as well as the right one and the test loses
  its edge.
- This is the mirror image of E095, where the crib carried too little information.
- The rule demands all three calibrations, so the result is VOID.

## Voynich (unscored, because VOID)
| Language | A: z, p (wrong cribs ≥ true) | B: z, p (wrong cribs ≥ true) |
|---|---|---|
| Latin | +0.02, 0.54 (53) | +0.42, 0.37 (36) |
| French/Occitan | +0.13, 0.51 (50) | +1.10, 0.12 (11) |
| Italian | +0.11, 0.54 (53) | +0.39, 0.39 (38) |
| German | +1.55, 0.06 (5) | −1.06, 0.79 (78) |
| Hebrew | −0.38, 0.74 (73) | +0.01, 0.61 (60) |
| Arabic | −0.01, 0.50 (49) | +0.02, 0.46 (45) |

- **Combined over the 12 configurations:** max-T p = 0.38.
- **No configuration stands out.** The true crib sits in the middle of the wrong cribs everywhere. The best is German A
  (p 0.06 alone), which is what chance gives with 12 tries.
- **In calibration**, a true crib scored 2 to 3 points of log-probability per sign above the wrong-crib average.
  **On Voynich** the gap is about 0 ± 0.3.

## What it means
- **The test is VOID**, so nothing is scored and the ledger is unchanged.
- **The unscored picture is flat.** On the real book, no zodiac crib in six languages opens a key that reads A or B
  better than wrong cribs do. A working crib would also have had to beat the E047 whole-book attack, which already found
  nothing in these languages (E049, E063).
- **The zodiac crib route is now bounded on both sides:**
  - with a free key, the zodiac text is too small to identify a key (E095);
  - with whole-book completion, the crib adds nothing the decoder would not reach without it (E095b).
- **What could still work:**
  - a crib that is longer or more certain than sign meanings (e.g. a known phrase);
  - a cipher class outside VOY23 (verbose, or order-changing).

## Ledger
No factor (VOID). M 0.4631, L 0.3604, C 0.0978, O 0.0788.
