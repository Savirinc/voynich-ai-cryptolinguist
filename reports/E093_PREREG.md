# E093 pre-registration (approach check 4 of 4): the simplest writing process, and do its free choices follow the pictures?

Written 2026-10-28, before the run. Script: `experiments/e093_explanation_model.py`. Output: `experiments/results/e093.json`,
`e093_run.log`, report `reports/EXPLANATION_MODEL.md`. Updates `LEDGER.md`.

## Question
Instead of asking "which language is it?", (1) what is the simplest word-writing process that reproduces the solid facts
(those that survived E092), and which facts does it fail to produce; (2) do the text's free choices follow anything outside
the text, namely the subject of the page (herbal, pharma, bathing, stars), when scribe, Currier language, sheet and
distance in the book are held fixed?

## Part 1: process ladder (exactly four models; no others)
Words are cut into front + middle + ending with the E074 lists (10 fronts, 20 endings, empty included; greedy: longest
ending, then longest front). The middle comes from a glyph chain starting at the front's last glyph.
| Model | Adds |
|---|---|
| P1 | one table of (front, ending); words independent |
| P2 | the table depends on line position (first / inside / last) |
| P3 | it also depends on the previous word's ending in the line (junctions such as q- after -y) |
| P4 | copying: probability c of reusing one of the last k words on the page, unchanged or (probability a) with one alternation e/ee, r/l, t/k, d±, q±; (c, a, k) chosen by likelihood on a 4×3×3 grid |
Held-out bits per word: fit on half the bifolios (alternating), score the other half; **P\*** = lowest. Samples of P1–P4
(5 seeds each, fitted on all DEV, Voynich's own page and line lengths) are scored on 13 items; an item is REPRODUCED iff
>= 4 of 5 samples pass:
| Item | Pass rule (Voynich value) |
|---|---|
| B1 book vocabulary | types within ±10% (6,077) and one-off share within ±0.03 (0.678) |
| B2 vocabulary at 150 words (E067) | |d_T| <= 0.5 and |d_H| <= 1 in Voynich sd |
| B3 ×6 small-scale battery (E068: WL, WLSD, H2, END5, R, NR) | each within 1 Voynich sd of Voynich |
| B4 family-level repeats (E066) | z <= generator median (0.55) |
| B5 common-word partners (E069 STAB) | between generator max 0.053 and language p10 0.083 (Voynich 0.073) |
| B6 content-word partners (E070 PSO) | below every language, 0.018 (Voynich 0.004) |
| B7 lines independent (E086) | |z| < 13 (half the lowest language) |
Spaces-mechanical is left out (E092: depends on the glyph cut).
**Verdict:** M HAS A WORKING PROCESS iff P\* reproduces all 13 → **M × 3**. Otherwise NO WORKING PROCESS, no factor
(E032 already counted a generator failing); the items P\* fails are listed as the facts a simple meaningless process
does not produce.

## Part 2: subject tracking
Page = its line-internal clean words (first and last word of each line dropped, so line-position habits and page layout do
not count). Similarity = cosine of word counts with the 50 commonest types removed. Pairs: same scribe (hand) and Currier
language, different bifolio, at least 2 pages apart; bins = distance quintiles. DELTA = weighted mean over (stratum, bin)
of [mean similarity of same-subject pairs − of different-subject pairs], weight min(n_same, n_other). z against 1,000
permutations of subject labels within stratum. DEV strata with two subjects: hand 1/A herbal 76 vs pharma 12; hand 2/B
herbal 20 vs bathing 17; hand 3/B herbal 6 vs stars 18.
- **Known answers:** Vulgate and KJV in 200-word chunks (every k-th, about 170 pages), subject = genre (law, history,
  wisdom, prophets, gospels, letters). Each must give z >= 3.
- **False-claim controls:** the Timm–Schinner generator and a P\* sample, each poured into Voynich's line structure and
  given Voynich's page labels. Each must give z < 2.
- **Verdict:** VOID unless both hold. Else Voynich z >= 3 TRACKS SUBJECT → **M × 1/3**; z < 1 NO TRACKING → no factor
  (E085 already counts the same-plant absence); otherwise INCONCLUSIVE, no factor.

## Disclosed
- The DEV page counts per (hand, Currier, subject) above were looked up to fix the strata. A smoke run (1 sample per
  model, 50 permutations) was executed to check the pipeline; its results were not read. Only its runtime and three
  numpy matmul warnings were looked at; the similarity matrix was checked finite and equal to an independent cosine
  computation (max difference 2e-15), so the warnings are spurious.
- Simplifications declared: each word has one deterministic cut (no sum over cuts); the middle chain ignores the ending;
  smoothing constants fixed (beta 5, add 0.1).
