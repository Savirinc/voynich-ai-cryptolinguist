# E114 (Arham, Reddit R10): can a dice word generator make the Voynich's fingerprint?

Pre-registration `E114_PREREG.md` (sha256 80bb2de8…), script `experiments/e114_dice_generator.py` (sha256 6f374605…).
Results `experiments/results/e114.json`, log `e114_run.log`. Run 2026-10-31, 8,221 s; 7,560 dice books plus 10 for the
seed check.

## Verdict
- **CLASS FAILS:** the best of 252 settings fails 7 of 13 features; the seed check (seeds 11–20) fails 9.
- **Factor:** M × 0.90 (dice share of M 0.15 × 1/3).

## Known answers first (VALID)
| Check | Best set | Fails | Needed |
|---|---|---|---|
| Planted dice book (d66, every 10 lines, 15/45/30) | d66, every 12 lines, 17/51/34 | 1 (type_hapax) | ≤ 1 |
| Copy generator | 2d6, every 3 lines, 13/39/26 | 6 | ≥ 2 |

## Voynich
**Fails per set:**

| Fails | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|
| Sets | 3 | 21 | 47 | 75 | 52 | 54 |

**Best by dice type:**

| Dice | Fewest fails |
|---|---|
| d6 | 7 |
| 2d6 | 7 |
| d66 | 9 |

**Best set:** 2d6, new tables every page, lists 20/60/40.

| Feature | Voynich | Dice (mean) | z |
|---|---|---|---|
| R (repeats right after itself) | 2.65 | 5.74 | −2.7 |
| NR (near-repeats) | 2.12 | 3.15 | −4.5 **fail** |
| distinct words | 6,077 | 10,721 | −37.5 **fail** |
| h2 (next-letter uncertainty) | 2.10 | 2.58 | −11.6 **fail** |
| I_word (word clumping) | 0.387 | 0.291 | +9.4 **fail** |
| top_word | 0.285 | 0.127 | +11.5 **fail** |
| once-used share of words | 0.678 | 0.498 | +13.2 **fail** |
| Zipf slope | −0.65 | −0.22 | −20.3 **fail** |
| word length, PERS_30, COV_30, NSUF95, DIST | — | — | within 3 |

**Fails across all 252 sets:**
- every set fails the once-used share;
- 249 fail Zipf;
- 247 fail word clumping and top_word.

Unscored: lines-independence z +0.32 for the best set (Voynich ≈ 0; dice lines are independent too).

## What it means
Independent dice rolls spread use too evenly over the possible combinations.

**What dice books get wrong:**
- **Common words:** the Voynich has a few very common words (Zipf slope −0.65) and many once-used ones. Dice books
  have a flat spread (−0.22).
- **Distinct words:** dice books have far too many different words, yet a smaller share of them used only once.
- **Letter order:** the next letter is less predictable than in the Voynich, because the slots join freely.

**Repeats:** re-filling the tables makes words repeat locally, as planned. The settings that get R right then
overshoot it or miss the rest.

**What this excludes:** no setting of one roll per slot comes close. Within this scope, independent dice per slot
(d6, 2d6, d66; never to every line; lists 8/24/16 to 25/75/50) is excluded.

**Not excluded (rule 11):**
- dice with line-position tables;
- dice whose later slots depend on earlier rolls;
- dice combined with copying.

## Ledger
**M × (1 + 0.15 × (1/3 − 1)) = M × 0.90**, renormalised:

| M | L | C | O |
|---|---|---|---|
| 0.7215 | 0.1961 | 0.0369 | 0.0455 |
