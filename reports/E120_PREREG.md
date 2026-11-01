# E120 pre-registration (Arham "do 1", 2026-11-01): can one meaningless writing process reproduce the solid facts?

Script `experiments/e120_working_process.py` (sha256 in the commit). The process, the grid, the 10 held-out facts and
their bands are in the script's docstring and fixed now.

## Why
M leads the ledger only because language signals are absent. No meaningless process has yet reproduced the text:
- Timm generator: 7/13 battery fails (E032);
- E093 ladder: 5/12;
- dice generator: 7/13 (E114);
- human gibberish: 1/5 (E068).

This is the strongest test M can win, and it can also fail it.

## Design
- **Process P5, "habit writer":**
  - built from the published rules of quimqu's 2026 generator (`WEB_SWEEP.md` #9) and Parisel's per-folio habit
    switch (#4);
  - two habit states (Currier A and B), sessions per sheet, copy-and-change from nearby words or the word above, habit
    words and new words from a letter chain;
  - line-start, line-end and paragraph-first habits taken from the Voynich itself.
- **Stage 1, tuning:** the 13-feature battery only, 32 settings × 2 seeds; best = fewest fails.
- **Stage 2, held-out:** 10 facts never computed on any generated book before this run:
  - phrase reuse, 4-word repeats, pair asymmetry, family-level repeats;
  - richness at 150 tokens, sheet clustering, page-opening surprise, line independence;
  - common-word partners, letter link.

  Bands as in the docstring. 5 fresh seeds; rule 8 clause for any fact near a band edge.

## Decision
| Outcome | Rule | Factor |
|---|---|---|
| WORKING PROCESS | battery ≤ 1 fail and ≥ 9/10 held-out | M × 3 |
| PARTIAL | battery ≤ 2 and 6–8 held-out | none |
| NO WORKING PROCESS | otherwise | M × 0.9 (as E114) |

## Seen beforehand (development, stage 1 only; disclosed in full)
- **Seven design rounds on the battery alone.** Each change was made after seeing battery numbers:
  1. a fixed lexicon;
  2. composed words added;
  3. the A/B habit states;
  4. the letter chain;
  5. session strength in the grid;
  6. a cap on position ratios (reverted because it was worse);
  7. the final grid.
- **Best development result:** 5 fails (NR, h2, top_word, PERS_30, type_hapax) at COPY 0.4, MUT 0.5, LEXP 0.35,
  LAG 16, SIGMA 0.1. The tuning seeds are the same as in development, so **stage 1 will again give 5 fails.**
- **The verdict is therefore already fixed:** NO WORKING PROCESS, M × 0.9. Stage 2 is still run as declared. It says
  which held-out facts a tuned habit writer reproduces, and how close M's best process comes.
- **No held-out fact** was computed on any generated book. The Voynich values of the held-out facts are known from
  E059, E066, E067, E069, E086, E100, E104, X115 and X117.
