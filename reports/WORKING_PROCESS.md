# E120: can one meaningless writing process reproduce the solid facts? (Arham, step 1)

Pre-registration `E120_PREREG.md` (sha256 8018d938…), script `experiments/e120_working_process.py` (sha256 5001c1f5…),
results `experiments/results/e120.json`, logs `e120_run.log`, dev `e120_dev.json`. Run 2026-11-01, 87 s.

## The process
**P5, the "habit writer"** (after quimqu 2026 and Parisel 2026):
- **Habits:** two habit states (Currier A and B), with sessions per vellum sheet.
- **Copying:** words are copied and changed from nearby words or the word directly above.
- **New words:** habit words, plus new words from a letter chain.
- **Positions:** line-start, line-end and paragraph-first habits taken from the Voynich.

Its best setting (COPY 0.4, MUT 0.5, LEXP 0.35, LAG 16, SIGMA 0.1) writes, for example, `pin dair tod / pin olchedyo pin`.

## Stage 1, tuning (13-feature battery)
**5 fails** (NR, h2, top_word, PERS_30, type_hapax). That is better than the Timm generator (7) and the dice generator
(7), but short of the ≤ 1 needed.

## Stage 2, held-out facts (5 fresh seeds; computed for the first time)
| Fact | Voynich | Band | Process | Reproduced |
|---|---|---|---|---|
| H1 phrase reuse Q3 | 12.9 | 9.7–16.1 | 2.0 | no: the Voynich reuses *more* 3-word phrases than this process |
| H2 repeated 4-word phrases | 0 | ≤ 20 | 0.4 | **yes** |
| H3 pair asymmetry | 0.18 | ≤ 0.30 | −0.02 | **yes** |
| H4 family-level repeats z | −1.1 | ±2 | −0.8 | **yes** |
| H5 distinct words per 150 | 111 | 103–119 | 96 | no (like the copy generator, 94) |
| H6 sheet vs reading-order clustering | 1.29 | ≥ 1.10 | 0.94 | no |
| H7 page-opening surprise | +0.89 | 0.6–1.2 | −0.03 | no |
| H8 lines independent z | +0.1 | ±3 | −0.1 | **yes** |
| H9 common-word partners STAB | 0.072 | 0.055–0.083 | 0.062 | **yes** |
| H10 letter link (MIDMI) | 12.1e-4 | 8.3–16e-4 | 5.6e-4 | no |

**Verdict: NO WORKING PROCESS** (battery 5 fails, held-out 5/10), **M × 0.9** as pre-registered (the factor was fixed by
stage 1, disclosed beforehand).

## What it teaches
- **What copying explains:** single-word copying with small changes gives for free the absence of long phrases,
  generator-like pair order, family-level repeats, independent lines and weak common-word partners. These five need
  no meaning.
- **What it does not explain, and the hardest open facts for M:**
  1. The Voynich has *some* short-phrase reuse (Q3 12.9) that pure word-by-word copying lacks.
  2. Its vocabulary is richer at 150 tokens.
  3. Pages on the same sheet share vocabulary more than the process's sessions give.
  4. Page openings are strongly surprising. Position habits copied from the Voynich did not reproduce this, so the
     opening effect is more than a habit of front pieces.
  5. Its letters are linked over 48–512 characters about twice as strongly.
- **Limit:** a different process, or more design rounds, might do better. This is one family, honestly tuned.

## Ledger
M × 0.9: **M 0.9130, L 0.0612, C 0.0116, O 0.0142** (was 0.9210 / 0.0556 / 0.0105 / 0.0129).
