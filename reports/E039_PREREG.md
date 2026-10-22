# E039 pre-registration (attack step 1c): scribe habit or location habit?

Written 2026-10-22, before the run. Script: `experiments/e039_scribe_habits.py`. Working assumption L. This is a
measurement, with no ledger factor.

## Question
E038 found that the d± and q± forms sit on different pages, and that t/k leans the same way. **Is that because
different *scribes* spelled differently, or because different *parts of the book* (topics or sections) use different
forms?**
- If it's scribes, these are spelling habits that can be normalised away before any reading attempt.
- If it's location, they may carry content.

## Data
- **Text:** Voynich DEV prose, clean tokens.
- **Scribe:** the hand given in the ZL transliteration, which follows Davis's five scribes.
  - Hands 1, 2, 3, 4 and 5 are used. Tokens with no assigned hand ('@') are dropped.
  - Hand 1 is essentially Currier A; hands 2, 3 and 5 are B.
- **Location:** the quire.
- **Separating the two:**
  - Most quires have one hand, but quires D, E, F, G, H, N and Q have two or three. That is what makes a "same quire,
    different scribe" comparison possible.
  - Hand 1 spans many quires, and hands 2 and 3 several, which allows a "same scribe, different quire" comparison.
- **Pairs:** E038's minimal pairs for all five alternations, with both forms seen at least 5 times. A word in several
  pairs of one alternation is kept in its first pair only.

## Statistics
For every token of a pair word, record which form it is (f), its pair (p), its hand (h) and its quire (q). Then
measure, in bits:
- **E_hand:** I(f; h | p), whether the form depends on the scribe;
- **E_hand_loc:** I(f; h | p, q), whether it depends on the scribe *within the same quire*;
- **E_loc_hand:** I(f; q | p, h), whether it depends on the quire *within the same scribe*.

Each is given as the excess over 500 permutations that shuffle f within the conditioning cells. One-sided p-values
are used, with α = 0.01.

| Verdict | Rule | Meaning |
|---|---|---|
| SCRIBE HABIT | E_hand_loc significant, E_loc_hand not | The scribe decides the form |
| LOCATION HABIT | E_loc_hand significant, E_hand_loc not | The part of the book decides, whoever writes |
| BOTH | both significant | |
| ENTANGLED | neither conditional significant, but E_hand significant | Scribe and location coincide too much to separate |
| NO PATTERN | none significant | |

Also reported: the share of the "with" form (with d, q, k, l or ee) by hand, weighting each pair once.

## Controls (planted labels on the e/ee pair tokens)
| Control | How it's built | Expected |
|---|---|---|
| Planted scribe habit | form = 1 for hand-1 tokens, 0 otherwise; each label flipped with probability 0.1 | SCRIBE HABIT |
| Planted location habit | form = 1 in quires D–H, 0 otherwise; each label flipped with probability 0.1 | LOCATION HABIT |

If either control gives the wrong verdict, the test is **VOID**.

## What follows
| Result for d and q | Next step |
|---|---|
| SCRIBE HABIT | Normalise these forms per scribe when re-measuring the inventory (step 1d) |
| LOCATION HABIT | Keep them; they may carry content. Look at what distinguishes those sections. |
| ENTANGLED | Cannot be separated with this manuscript. Keep both readings open. |

## What was seen before writing this (disclosed)
- Counts of tokens by hand, by hand × Currier, and by quire × hand (to check that the design can separate them).
- E038's results.
- The classifier was checked on a toy dataset with planted labels: 200 permutations gave the expected verdicts. A
  50-permutation check could not reach α = 0.01, which is why the run uses 500.
