# E036 pre-registration (ledger test 7): free invention of spellings, with the seed check built in

Written 2026-10-21, before the run. Script: `experiments/e036_free_invention.py`. Updates `reports/LEDGER.md`.

## Question
E035/E035b established two things about spelling variation on Indonesian, in which common words reuse a few
spellings:
- **In all 10 runs it reproduced** the exact copies, the near-copies and the flat Zipf head.
- **It systematically failed** on two features:
  - too few words seen once (about 0.58 against Voynich's 0.68);
  - too much persistence (PERS_30 about 0.49 against 0.26).

Both gaps say that Voynich's variant spellings are more scattered: most are used only once. **Does a model in
which spellings are freshly invented, not reused, close those gaps?**

## Model (one parameter, p; replaces E035's model rather than adding to it)
- **First time a word appears:** written in its base spelling.
- **Every later use:** with probability p, written with a **fresh** spelling, never used before for that word.
  Otherwise it uses the base spelling.
- **A fresh spelling** is one random edit of the base, exactly as in E035 (substitute, insert or delete one letter,
  2 : 1 : 1, letters from the window's own frequencies).

## Design: E035b's design, with the seed check built in
- **Kept from E035b:** the 12 Bibles and their E033 windows; the 9 features (E033's 8 plus NR); the z rule
  (|z| > 3 fails, sd floor as E033); a best text per replicate; Voynich's NR recomputed with each eval seed.
- **p:** fitted on types only, per text and per replicate, from the grid {0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06,
  0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6}.
- **Replicates:** 10, with fit seed 36100 + r and eval seed 36600 + r. A replicate matches if its best text fails at
  most 1 of 9.

| Outcome | Replicates that match (of 10) | Bayes factor |
|---|---|---|
| ROBUST MATCH | 8 or more | L × 10, C × 3 (reasoning as in E035) |
| UNSTABLE | 3–7 | none |
| NO MATCH | 2 or fewer | none |

## Prediction stated in advance (an honest risk)
- In E035, the flat Zipf head came from splitting frequent words across *several reused* spellings.
- Here, every word keeps (1 − p) of its uses in the base spelling, so the top words may stay dominant, and the Zipf
  head may go back to failing.
- Fresh spellings should, though, raise the share of words seen once and lower persistence. I expect this model to
  trade one failure for another, but it is run as stated.

## Guard against trying models until one fits
- This is the **second and last** variation model in this family.
- Whatever the outcome, no third variant (mixtures, Pitman–Yor, edit patterns) will be scored unless a newly
  measured fact, not a near miss, calls for it.
- Recorded tries so far: E035, a reused-spellings model whose score was withdrawn by E035b; and E036.

## What was seen before writing this (disclosed)
- E035 and E035b outputs.
- The new model has not been run on anything.
