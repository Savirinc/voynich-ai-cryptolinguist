# E048 pre-registration: is the word order inside Voynich lines informative, or scrambled?

Written 2026-10-24, before the run. Script: `experiments/e048_word_order.py`. Runs after E047 finishes (one job at a
time).

## Question
C21 says Voynich doesn't avoid identical neighbours: AS ≈ 1, which is exactly what shuffling words *within lines*
produces. Hebrew scripture already has Voynich's level of same-line recurrence (E043). The owner asked: could the
text be **made secret by scrambling word order**, for example a Hebrew text with words rearranged within each line?

**What is measured:** whether neighbouring words inside Voynich lines carry information about each other beyond
merely sharing a line.

## Structural sub-hypothesis (new, set now)
| Hypothesis | Meaning | Prior |
|---|---|---|
| ORDER-INTACT | word order within lines is as written in the underlying text | 0.85 |
| ORDER-SCRAMBLED | the words inside lines were rearranged (a transposition), with the first and last word possibly kept in place | 0.15 |

**Why ORDER-SCRAMBLED starts low.** E025 found strong line-start and line-end habits, which a full shuffle would
erase. That is why the measure below keeps the first and last word fixed.

## Statistic
- **Word classes:** each text's 300 commonest words stay as themselves; rarer words become "rare word ending in x".
- **I:** the mutual information (bits) between neighbouring word classes within lines.
- **D_int** = I(observed) − mean I over 20 *interior* shuffles (words 2 to L−1 of each line rearranged; first and
  last kept). This is the information carried by interior word order.
- **Q** = D_int(Voynich) ÷ the median D_int of the real, unscrambled texts.
  - About 1: order as informative as real texts.
  - About 0: order looks scrambled.

## Texts
- **Real:** Hebrew Genesis–Exodus, Hebrew Psalms, Latin Genesis–Exodus, Latin hymns, Apicius + Cato + Varro, the
  Turkish Bible and the Indonesian Bible.
- **Lines:** all real texts are cut into pseudo-lines with Voynich DEV's line lengths, in windows of 8,806 tokens (up
  to 10, seed 48048).
- **Scrambled controls:** the first 3 windows of each real text with words fully shuffled within lines.
- **Copy generator:** its own lines (reported only).
- **Voynich:** Currier A, and Currier B as 10 A-sized runs.

## Decision
| Outcome | Rule | Factor |
|---|---|---|
| VOID | the method fails to separate: any scrambled control has Q > 0.2, or any real text has Q < 0.5 | none |
| ORDER LOOKS SCRAMBLED | Voynich A's Q ≤ 0.2 | ORDER-SCRAMBLED × 10 |
| ORDER INTACT | Voynich A's Q ≥ 0.5 | ORDER-SCRAMBLED × 1/10 |
| PARTIAL ORDER | otherwise | none |

Currier B is reported alongside.

## Consequence for step 3b
- **If order looks scrambled,** the Voynich attack must score each line as a bag of words, or undo the scrambling.
- **If order is intact,** the attack may use word order as usual.

## What was seen before writing this (disclosed)
- E025's line-position effects, and E043–E046.
- No word-order statistic has been computed on any text.
