# E098 (Arham): can any of five untested period cipher classes make the Voynich's fingerprint?

Pre-registration `E098_PREREG.md` (sha256 239c53fb…), script `experiments/e098_cipher_classes.py` (sha256 5878e4d9…).
Results `experiments/results/e098.json`, log `e098_run.log`. Run 2026-10-30, 12,120 s; 7,350 cipher books plus
50 for the seed checks.

## Verdict
- **K1, K3, K4, K5: CLASS FAILS.**
- **K2: PARTIAL**, because its seed check gave 4 fails instead of 5.
- **Factor: C × 0.653.**

## Known answers first (all five classes VALID)
| Class | Planted book reproduced (best set, fails) | Generator not reproduced (best set, fails) |
|---|---|---|
| K1 nomenclator | 0 | 4 |
| K2 letters rearranged in words | 0 | 5 |
| K3 null words | 0 | 4 |
| K4 rotating tables | 0 | 7 |
| K5 abbreviation then cipher | 0 | 5 |

## Voynich (245 sets per class, the best shown)
| Class | Best set | Fails | Failing features (z) | Seed check | Verdict |
|---|---|---|---|---|---|
| K1 | 50 code words, Hebrew | 5 | R +7.9, h2 −17.1, hapax +3.2, Zipf +3.5, DIST +7.4 | 5 | CLASS FAILS |
| K2 | sorted units, Hebrew | 5 | R +7.7, NR +8.1, h2 −5.1, hapax +6.3, DIST −4.1 | 4 | PARTIAL |
| K3 | 10% null words, Hebrew | 6 | R +10.8, NR +5.1, h2 −17.6, PERS −5.4, NSUF −4.9, DIST +6.2 | 7 | CLASS FAILS |
| K4 | new table every 4 lines, German | 6 | length −10.4, types −10.8, h2 −22.8, Zipf −6.8, NSUF −10.2, DIST +32.6 | 6 | CLASS FAILS |
| K5 | vowels dropped, Hebrew | 5 | R +12.8, NR +3.2, h2 −17.6, Zipf +3.7, DIST +4.6 | 7 | CLASS FAILS |

Positive z means the Voynich has more of the feature than the cipher books; negative, less.

**Two failures shared by every class:**
- **R:** the Voynich repeats a word right after itself far more often than any of these ciphers do.
- **h2:** the Voynich's next glyph is much more predictable (lower letter variety) than any of these ciphers make it.

Rotating tables fail in the opposite direction: too many distinct words, glyph variety too high.

**Unscored:** lines-independence z for the best sets is +3.6 (K2) to +47 (K4); Voynich ≈ 0. Only K2 comes near.

## What it means
None of the five period cipher classes can produce the Voynich's profile with any declared setting, plaintext
language or seed: not even with code words and filler words taken from the Voynich itself. The closest, letters sorted
inside each word, still fails 4–5 facts, chiefly repeats and glyph predictability. Excluded within this scope:
nomenclators, null-word fillers, Alberti-style rotating tables and abbreviate-then-encipher, over Latin, Italian,
German, Occitan and Hebrew with 23 output units.

Not excluded: these classes over other languages or other output units, combinations of classes, and cipher designs
not listed (the untested 0.40 of C).

## Ledger
C × (1 + 0.20(1/3−1) + 0.08·0 + 0.12(1/3−1) + 0.10(1/3−1) + 0.10(1/3−1)) = C × 0.653.

- **New ledger:** M 0.4897, L 0.3594, C 0.0676, O 0.0833.
- **Shares within C, renormalised:**

  | K1 | K2 | K3 | K4 | K5 | Rest |
  |---|---|---|---|---|---|
  | 0.102 | 0.122 | 0.061 | 0.051 | 0.051 | 0.612 |
