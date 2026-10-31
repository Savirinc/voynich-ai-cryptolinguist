# E114 pre-registration (Arham, Reddit R10, 2026-10-31): can a dice word generator make the Voynich's fingerprint?

Script `experiments/e114_dice_generator.py` (sha256 in the commit). Locked before the Voynich is scored.

## Question
Reddit R10 (threads czs0g6, iuvmly): the Voynich words could have been made by rolling dice, one die per slot of the
word, with no copying from earlier text. This is a period-plausible meaningless (M) process that has never faced our
battery. It is a test M can win.

## The process (declared now; no other variants)
- **A word = front + middle + ending.** Each slot is chosen by one roll from its own table. An empty word is re-rolled.
- **Master piece lists:** taken from the target itself with E074's list builder (commonest fronts, middles and endings,
  each list including the empty piece). Pieces are weighted by how often the target's tokens use them. Tokens are
  parsed by the longest front, then the longest ending. This is generous to M: a designer could have chosen exactly
  these pieces.
- **Dice (3):**
  - **d6:** 6 entries per table, rolled uniformly. Entries are drawn from the master list by weight, without
    replacement.
  - **2d6:** 11 entries for the sums 2–12, triangular odds. The first-drawn (usually commonest) piece sits on 7.
  - **d66:** two dice as row and column, 36 cells. The cells are filled by weighted draws, so common pieces get several
    cells.
- **Re-filling the tables (14):** never (book); every page; or every 64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2 or 1
  line(s). Re-filling is a fresh weighted draw from the same master lists, as a writer making new tables would do.
- **Master list sizes (6):** front/middle/ending 8/24/16, 10/30/20, 13/39/26, 17/51/34, 20/60/40, 25/75/50.
- **Sets:** 3 × 14 × 6 = 252 sets, 10 seeds each (seeds 1–10). Output is poured into the Voynich DEV page and line
  shape (173 pages, 28,841 tokens; LOCKED_TEST leaves excluded).

## Yardstick (as E032, E062, E098)
- **Features:** E032's 13 features (R, NR, wl_mean, types, h2, I_word, top_word, PERS_30, COV_30, type_hapax,
  zipf_slope, NSUF95, DIST).
- **Score:** per set, z = (target − set mean) / max(sd, 2%|target|, 0.01). A feature fails iff |z| > 3. The best set
  is the one with the fewest fails.
- **Unscored:** the E086 lines-independence z for the best set (seeds 1 and 11), and sample lines.

## Known answers first
- **Planted:** a dice book made from the Voynich's pieces with an off-grid setting (d66, re-fill every 10 lines,
  lists 15/45/30, seed 777). It must be reproduced by the best set (≤ 1 fail). The search re-derives the pieces from
  the planted text.
- **False claim:** the copy generator (E032 output in the Voynich shape) must not be reproduced (best set ≥ 2 fails).
- **Validity:** if either check fails, the test is VOID.

## Decision table (Voynich)
| Outcome | Rule | Factor on the dice share of M |
|---|---|---|
| REPRODUCES | best set ≤ 1 fail, and again ≤ 1 with seeds 11–20 (rule 8) | × 3 |
| CLASS FAILS | every set ≥ 5 fails, and the best set again ≥ 5 with seeds 11–20 (rule 8) | × 1/3 |
| PARTIAL | otherwise, or the seed check disagrees | none |
| VOID | a known-answer check failed | none |

- **Share of M for dice and slot-table generators:** 0.15 (judgement, fixed now; the rest of M is copy-and-change,
  human free invention, grilles and others).
- **M's change:** M × (1 + 0.15 × (factor − 1)), then all four renormalised.
  - REPRODUCES: M × 1.30.
  - CLASS FAILS: M × 0.90.
- **Rule 8:** the seed check with seeds 11–20 is part of the rule above, so a verdict near a boundary cannot stand on
  one seed set.
- **Honest limit:** a failure excludes only these dice designs (one roll per slot, independent rolls, these table
  sizes and re-fill rates), not every table-based generator (rule 11). Dice with line-position tables, or dice combined
  with copying, are not tested here.

## Seen beforehand
- **Already known:** the Voynich's 13 feature values (E032, E062, E098). Its R is 2.65: words repeat right after
  themselves 2.65 times as often as chance.
- **Expectation:** independent rolls give R near 1 when the tables never change. Re-filling the tables is the only way
  this process can raise R, because it makes words local. This was understood before locking, and it is why re-fill
  rates are in the grid.
- **Development (smoke runs on synthetic targets only; no Voynich features computed):**
  - First grid (lists 10/30/20 and 20/60/40 only; re-fill book, page, 64, 32, 16, 8, 4, 2, 1; plant re-filled every
    12 lines): the planted book was not reproduced (3 fails: types, I_word, type_hapax), so the test would have been
    VOID.
  - Finer list sizes (six, as now): still 2 fails (R, type_hapax).
  - Finer re-fill grid (as now), with the plant moved off-grid to every 10 lines: plant reproduced (1 fail,
    type_hapax). The generator was not reproduced (7 fails) in every smoke run.
- **Built from Voynich data:** the planted book uses the Voynich's own pieces, as any target does.
