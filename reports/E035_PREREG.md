# E035 pre-registration (ledger test 6): real languages with free spelling variation

Written 2026-10-21, before the run. Script: `experiments/e035_spelling_variation.py`. Updates `reports/LEDGER.md`.

## Question
No measured text has Voynich's four word habits together (E031, E033, E034):
1. exact copies of a neighbouring word (R 2.65);
2. near-copies of a neighbouring word (NR, about 2.1);
3. a rich vocabulary (6,077 distinct words, 68% seen once);
4. a flat Zipf head (−0.65, against −0.79 to −1.12 everywhere else; C11).

One added part could produce all four: **the same word written in several spellings, freely**, in a language that
doubles words. A common word spelled several ways splits its count, which flattens the head and adds rare forms. A
doubled word written with two different spellings becomes a near-copy. **Does adding this one part to a real text
reproduce Voynich?**

## Variation model (fixed now; one parameter, α)
Inside each window, word by word in reading order:
- **First time a word appears:** written in its base spelling.
- **Later times:** either reuse a spelling already used for that word, in proportion to how often each has been
  used, or, with probability α ÷ (n + α), get a **new spelling**. Here n is the number of times the word has been
  seen so far.
- **A new spelling** is one random edit of the base spelling:
  - substitute, insert or delete one letter, in the ratio 2 : 1 : 1;
  - the letter is drawn from the window's own letter frequencies;
  - it is never the same as a spelling already used for that word.

Frequent words end up with about α·ln(n) spellings, and rare words keep one. This is the simplest model of
"scribes spell common words several ways" that I could write with one parameter.

## Fit, then test
- **Texts and windows:** E033's 12 Bibles, using exactly E033's windows (the same seed-33033 draw).
- **Fit:** for each text, choose α from the grid {0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.65, 0.8, 1, 1.25,
  1.5, 2, 2.5, 3, 4, 5}. Pick the value whose window-mean number of distinct words (types) is closest to Voynich's
  6,077, using the fit seed.
  - Nothing else is fitted.
  - A text already above 6,077 at α = 0 (Latin) gets α = 0.
- **Test:** at the fitted α, with a fresh seed, compute 9 features per window:
  - E033's 8 features (R, types, I_word, top_word, PERS_30, COV_30, type_hapax, zipf_slope);
  - NR (E031).

  So 8 of the 9 are predictions. Types is counted too: if the grid cannot reach Voynich, that is a fail.
- **z rule:** as in E033, z = (V − mean) ÷ max(window sd, 2%|V|, 0.01). A feature fails if |z| > 3. The best text has
  the fewest fails, with ties broken by RMS z.
- **Voynich:** DEV, the same values as E033. NR is recomputed with E031's code on DEV lines.

**Why NR is allowed here although E033 dropped it.** Under the variation model, a near-copy is "the same word, with
a different spelling, next to itself". NR is a ratio against shuffled text, so the letters themselves cancel to first
order. The model can only raise NR above 1 where the base text has neighbouring repeats. That makes NR a real
prediction, not something built in by construction.

**What follows by construction (said now).**
- Variation cannot create word repeats. A text with no doubling (Latin, English) cannot match R.
- The real candidates are the languages that double words: Indonesian, Malay, and to a lesser extent Yoruba and
  Hausa.

## Decision
| Outcome | Rule | Bayes factor |
|---|---|---|
| VARIATION MATCHES | best text fails at most 1 of 9 | L × 10, C × 3 |
| PARTIAL | best text fails 2 | none |
| NO MATCH | best text fails 3 or more | none |

**Why these factors.**
- **A match would be strong evidence.**
  - It would be the first text to fit C11 (the flat head) and the near-copies, which no text and no generator has
    fitted.
  - It would do so with one parameter fitted on a different feature (types), so 8 features would be predictions.
  - That earns "moderate" (×10) for L, as proposed when the test was agreed.
- **C gets ×3, not ×10.** A cipher could produce variant spellings only through an extra glyph-level homophone
  layer, whereas ordinary scribal variation needs no added layer (Occam rule).
- **M gets no factor.** A generator could perhaps be tuned to the same output.
- **A failure gives no factor.** It removes one candidate mechanism for an unexplained fact, and that fact counts
  against L and M alike (E033, E032). The failure is recorded, not scored.

## Built-in check
At α = 0 the fit step must reproduce E033's mean types for every text. This is stored in the output.

## What was seen before writing this (disclosed)
- E033's features for all 12 Bibles at α = 0, and Voynich's values.
- The variation function was run once on a toy word list to check that it works. No real text was varied before
  this file was locked.

## Limits
- **The edit model is generic.** Real scribal variation is patterned (i/y, doubled letters, abbreviations), and only
  NR is sensitive to that.
- **Bibles are one genre.**
- **A match shows that the mechanism is sufficient, not that it is what happened.** It would say what kind of
  writing Voynich could be, not what it says.
