# E050 pre-registration: settle the Hebrew near miss, by statistics and by blind reading

Written 2026-10-24, before the run. Script: `experiments/e050_hebrew_nearmiss.py`. LOCKED_TEST is not used.

## Question
E049: under the Hebrew model, Voynich A decoded to lexrate 0.542.
- That is above every control so far (highest 0.472), but below the pre-set claim bar (0.572) and real Hebrew cracks
  (0.65–0.79).
- Is that because the text is Hebrew, or only because Voynich's short words and sign frequencies make *any* decode
  hit short Hebrew words?
- And, at the owner's request: **does the decoded text mean anything when read?**

## Part 1: null distribution (statistics)
- **Attack:** E047's validated attack and the Hebrew LM, unchanged.
- **Voynich A:** 3 independent attack seeds; the mean lexrate is used.
- **40 controls:**
  - **20 pseudo-Voynich-A texts.** Each is generated from a sign-level order-2 Markov model of Voynich A's own
    cleaned words. They use the same 23 signs and have the same word-shape statistics (mean 3.6 signs per word was
    checked), but contain no language. This is the decisive control.
  - **20 copy-generator samples** (random stretches of E032's output).
- **BEATS ALL:** Voynich A's mean lexrate is greater than every one of the 40 controls. The chance of that by luck is
  about 1 in 41.

## Part 2: blind reading (meaning)
The script writes **7 unlabelled passages** of 60 decoded words (Hebrew letters, no vowels), in a shuffled order:
- **3 Voynich A pages:** the first three DEV Currier-A folios with at least 60 words, decoded with the best-scoring
  Voynich key.
- **3 control passages:** the 3 highest-lexrate controls, which are the hardest comparison.
- **1 positive control:** real Hebrew from the E047 TEST books, written in a fresh secret 23-sign key with spelling
  slips, and decoded by the same attack.

The labels are saved to a separate file and are not looked at until the judges have answered.

**Judges.** Two independent Claude sub-agents, each in a fresh context, get the passages in the same order and this
exact prompt:

> You are given 7 passages, A–G, written in Hebrew letters without vowel points. Some may be meaningful Hebrew,
> possibly with spelling errors; others may be meaningless strings that only happen to contain real words. For EACH
> passage: (1) give a score from 0 to 10 for how much it reads as MEANINGFUL Hebrew — coherent phrases and grammar,
> not merely isolated real words (0 = no meaning, 10 = clearly meaningful text); (2) give a literal English
> translation attempt of its first 15 words, marking anything unreadable with '?'. Judge only the text itself. Return
> the scores as a JSON object {"A": score, ...} on the last line.

**Rules.**
- **A judge is VALID** if it scores the positive control higher than all 3 control passages.
- **MEANING DETECTED:** both judges are valid, **and** both score all 3 Voynich passages higher than all 3 control
  passages.
- **NOT DETECTED:** both judges are valid, but that condition fails.
- **VOID:** any judge is invalid. The reading test then cannot tell meaning from chance.

## Overall decision
| Part 1 | Part 2 | Conclusion |
|---|---|---|
| BEATS ALL | MEANING DETECTED | Hebrew goes forward to **E051**: the frozen key is applied once to the LOCKED_TEST leaves. That is where a ledger factor would be pre-registered. |
| anything else | anything else | **Hebrew letter by letter (the validated VOY23 class): searched, not found.** The E049 near miss is explained by surface statistics if the pseudo-Voynich controls reach it. |

There is no ledger factor in E050 itself.

## What was seen before writing this (disclosed)
- E049's numbers and its first 12 decoded Hebrew words.
- A check that the pseudo-Voynich generator reproduces word length (3.60 vs 3.57) and type richness.
- No attack on any pseudo-Voynich text, and no full Voynich decode, has been run or read.
