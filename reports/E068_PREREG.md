# E068 pre-registration: human gibberish against Voynich's other small-scale habits

Written 2026-10-25, before the run. Script: `experiments/e068_gibberish_battery.py`. Output:
`experiments/results/e068.json`, `e068_run.log`, report `reports/GIBBERISH_BATTERY.md`. Updates `LEDGER.md`.

## Question
E067 removed M's vocabulary objection at the 150-token scale: humans writing gibberish make as many fresh words as
Voynich. Arham's stated goal for this step: **either M is ruled down, or it is a solid two-way street between L and M.**
So the same 36 gibberish pages now face the rest of Voynich's habits that can be measured in 150 tokens, with the
languages and the copy generator as the two anchors. Vocabulary (T, H) is excluded, since E067 already scored it.

**Terms.** *Near-copy*: two neighbouring words that differ by one letter. *Back-to-back repeat*: the same word twice in
a row. *H2*: how predictable the next letter inside a word is (bits; lower = more predictable). *END5*: the share of
words ending in one of the five commonest final letters (how concentrated the endings are).

## Data (as E067)
GIB = first 150 tokens of the 36 gibberish texts; VOY = 200 random DEV windows; LANG = 60 Bibles × 20 windows (group
value = mean of the 60 language means); GEN = 20 generator stretches × 10 windows. Seed 68068.
**Script convention:** Voynich is measured in EVA letters (S0), as in every cross-script comparison so far (E031–E036).
E027 showed that reading glyph *groups* as units moves Voynich's letter statistics (H2, word length) into the
simple-syllable range; that caveat applies to WL, WLSD and H2 here and is stated in advance. R, NR and END5 do not
depend on it (END5 weakly).

## Features (6)
| Feature | What | Voynich at full scale (known) |
|---|---|---|
| WL | mean word length (letters) | 4.99 |
| WLSD | spread of word length | tight (C: binomial-like) |
| H2 | conditional letter entropy within words | 2.10, below all alphabets |
| END5 | share of tokens ending in the window's 5 commonest final letters | high (y, n, l, r, s) |
| R | back-to-back repeats ÷ chance, pooled over windows | 2.65 |
| NR | near-copies ÷ shuffled, pooled over windows (5 shuffles) | 2.10 |

## Decision
For each feature: v (Voynich), l (languages), g (gibberish), m (generator, reported). sd_v = sd across Voynich windows;
for the pooled R and NR, the sd of the pooled value over 200 bootstrap draws of 36 Voynich windows.
- A feature is **diagnostic** iff |v − l| ≥ sd_v (Voynich and the typical language are told apart at this length).
- On a diagnostic feature gibberish is **Voynich-like** iff |g − v| < |g − l| (nearer Voynich than the languages).

| Outcome (D = diagnostic features, need D ≥ 3) | Rule | Factor |
|---|---|---|
| VOID | D < 3 | none |
| **M FULL CASE** | Voynich-like on every diagnostic feature | **M × 3** |
| **M RULED DOWN** | Voynich-like on at most one | **M × 1/3** |
| TWO-WAY STREET | otherwise | none; which habits gibberish lacks are recorded |

**Seed rule:** if any diagnostic feature has |g − v| within 10% of |g − l|, or |v − l| within 10% of sd_v, the reference
windows are re-drawn with 10 seeds; ≥ 8 of 10 must agree, else TWO-WAY STREET. Gibberish windows are fixed.

**Why × 3.** Same proxies as E067 (modern writers, minutes of writing, 150 tokens). "Ruled down" is a factor, not an
exclusion: standing rule 11 forbids excluding by probability.

## Disclosed
- E045: gibberish AS 0.66 (back-to-back avoidance statistic, close kin of R) against Voynich 1.0 and languages ≤ 0.53;
  so R is expected to land between, and the rule will decide which side. E067's T and H values for all groups.
- Voynich's full-scale values above; nothing at 150-token windows has been computed for WL, WLSD, H2, END5, R or NR
  for any group.
- The judge was smoke-tested on fabricated groups in both directions. One attempt (standing rule 9).
