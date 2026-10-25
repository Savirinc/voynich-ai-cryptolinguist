# E067 pre-registration: does human-written gibberish grow vocabulary the way Voynich does?

Written 2026-10-25, before the run. Script: `experiments/e067_gibberish_vocabulary.py`. Output:
`experiments/results/e067.json`, `e067_run.log`, report `reports/GIBBERISH_VOCABULARY.md`. Updates `LEDGER.md`.

## Why
M's one missing piece is the vocabulary: Voynich has 6,077 distinct words in 28,841, 68% seen once, and every generator
we can run makes a poorer, more uniform word stock (E032, E064 Part B). Nobody has asked whether a *human* writing
meaningless pseudo-language makes a vocabulary like Voynich's. Gaskell & Bowern (2022) collected 38 such texts from
38 writers. They are short (79–480 tokens, median 269), so the comparison is made at a matched short length. Arham's
decision (2026-10-25): if M misses here, the work stays inside L and is evaluated there.

**Terms.** A *window* is a run of W = 150 consecutive tokens. T = distinct words in the window; H = share of its tokens
whose word occurs once in the window; BETA = how fast the vocabulary grows from 75 to 150 tokens (log2 of the ratio of
distinct words; 1 means every new word is new, 0 means none is). *d* = distance of a group's mean from the Voynich
windows' mean, in units of the Voynich windows' standard deviation.

## Data
- **GIB:** the first 150 tokens of each gibberish text with ≥ 150 tokens (36 of 38; DC_23 and DC_24 are shorter),
  lowercase, letters/marks/apostrophes only.
- **VOY:** 200 random windows of DEV in reading order (clean tokens).
- **LANG:** 60 Bibles (all on disk except cmn-cu89s, jpn1965, vie1934, lit, engWycliffe), E064's tokenizer, 20 random
  windows each; the group value is the mean of the 60 language means.
- **GBM:** Gaskell & Bowern's 71 meaningful texts (historical, modern, conlang, technical, abbreviated Latin), cleaned
  the same way, 10 random windows each (reported, not in the rule).
- **GEN:** 20 random stretches of the E032 copy-generator output, 10 windows each (reported, not in the rule).
Seed 67067.

## Decision
d is computed on T (primary) and H (secondary).
| Outcome | Rule | Factor |
|---|---|---|
| VOID | the languages are not separated from Voynich at this length: |d_T(LANG)| < 1 | none |
| **GIBBERISH LIKE VOYNICH** | |d_T(GIB)| ≤ 0.5 and |d_H(GIB)| ≤ 1 | **M × 3** |
| **GIBBERISH ON THE LANGUAGE SIDE** | d_T(GIB) has the sign of d_T(LANG), |d_T(GIB)| ≥ |d_T(LANG)|/2 and > 0.5 | **M × 1/3** |
| GIBBERISH BEYOND VOYNICH | opposite side from the languages, |d_T(GIB)| ≥ 1.5 (humans make vocabulary richer still; the objection to M is not removed, because the pattern differs) | none |
| INCONCLUSIVE | otherwise | none |

**Seed rule:** a d within 0.1 of any boundary → the reference windows (VOY, LANG) are re-drawn with 10 seeds; ≥ 8 of 10
must agree, else INCONCLUSIVE. The gibberish windows are fixed (first 150 tokens).

**Why × 3 only.** The writers are modern, wrote for minutes not years, and were asked for gibberish; 150 tokens is a
small window. The test is a proxy for a 15th-century habit, so it can only be weak evidence either way.

## Disclosed
- E045 used the same gibberish texts for one statistic (AS 0.66); no vocabulary measure has been computed on them.
- Voynich's whole-text vocabulary facts (6,077 types, 68% one-offs) and the generator's (3,961, 52%) are known; nothing
  at 150-token windows has been computed for any group.
- Known-answer expectation written in advance: at 150 tokens the generator should fall below Voynich on T (it copies
  nearby words), and the languages below Voynich (fewer one-offs); if the languages do not separate, the test is VOID.
- The judge was smoke-tested on fabricated windows (random vocabularies of 400 vs 120–150 words) in both directions.
- One attempt (standing rule 9).
