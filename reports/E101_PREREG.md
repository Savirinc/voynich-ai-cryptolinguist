# E101 pre-registration: where are the glued-looking words? (A) line ends, (B) the bathing section (Arham, 2026-10-31)

## Question
Reddit idea R2 says rare Voynich words are two words written without the space. An unscored census (below, "seen
beforehand") showed that the cut works for many rare words but cannot by itself separate glue from word-building. Arham
asked for two targeted checks:
- **(A)** Are glued-looking words more common at **line ends** (squeezing when the line runs out), beyond what
  meaningless copying gives, and as much as planted line-end joins give?
- **(B)** Does the **bathing section** (B) have more glued-looking words than herbal (H) and stars (S), at the same word
  length?

## Definitions
A token is **GLUED** if it is ≥ 4 characters long, its word occurs ≤ 2 times in the whole text, and it cuts into two
pieces of ≥ 2 characters, each a word occurring ≥ 2 times. Single-glyph pieces (y, s, d, l, r, o) are excluded so that
ordinary word-endings and front pieces do not count.

## Data
- **Voynich:** DEV prose, clean tokens, 3,406 lines, 28,841 tokens, with LOCKED_TEST leaves excluded. Lines are
  labelled by illustration (H 9,762 tokens, S 9,959, B 5,489).
- **Generator controls:** 10 copy-generator stretches (E032 default).
- **Language controls:** 5 languages (latVUC, ita1885, deu1912, ces1613, turytc), each cut to 28,841 tokens.
- All controls are poured into the Voynich line lengths. They inherit each Voynich line's section label.

## Procedure (`experiments/e101_glue_where.py`)
### Part A: line ends
- Use lines of ≥ 3 words. D = GLUED rate of line-last tokens − GLUED rate of middle tokens (tokens ≥ 4 characters).
- **Known answer:** in each control, with probability 0.15 per line, the last two words are joined.
- **Validity:** the 10th percentile of D in planted generator stretches > the maximum of D in unplanted generator
  stretches.

| Outcome | Rule |
|---|---|
| SQUEEZE-LIKE | Voynich D ≥ planted-generator p10 and > unplanted-generator max |
| NO SQUEEZE | Voynich D ≤ unplanted-generator p90 |
| BETWEEN | otherwise |
| VOID | validity fails |

- **Rule 8:** if Voynich D is within 0.5 sd of a boundary (sd from 200 line bootstraps), run 10 line bootstraps; at
  least 8 must agree.
- **Unscored:** D within H, S and B separately; mean word length of line-last vs middle tokens.

### Part B: the bathing section
- For each section, rate = GLUED share of its tokens (≥ 4 characters), standardised to the text's own length mix
  (lengths 4–10; 10 covers 10+).
- d = rate_B − mean(rate_H, rate_S). Z = d / sd, with sd from 200 bootstraps of lines within each section.
- **Known answer:** delete 15% of the within-line spaces in the B-labelled lines only.
- **Validity:** planted generator Z > 2 in ≥ 8 of 10, and unplanted generator Z ≤ 2 in ≥ 8 of 10.

| Outcome | Rule |
|---|---|
| B GLUES MORE | Voynich Z > 2 |
| B NOT SPECIAL | Voynich Z ≤ 2 |
| VOID | validity fails |

- **Rule 8:** if Voynich Z is within 0.5 of 2, run 10 line bootstraps; at least 8 must agree, otherwise UNDECIDED.
- **Interpretation, fixed now:** B GLUES MORE means B has more glue-shaped words at the same length. This could come
  from real joins or from B's word-building; the text alone cannot separate the two (see below). If Part A also finds
  SQUEEZE-LIKE within B, that points towards joins.

## Bayes factors
**None for either part.** Glued words, squeezing and section habits fit M, L and C equally. They describe how the text
was written, not whether it means something. Results are recorded as measured facts.

## Seen beforehand
- **Failed yardsticks:** three yardsticks for "are rare words joins?" failed on planted joins in generator text,
  although they worked on languages. Those drafts were not locked. They are kept in the session scratchpad as
  `e101_draft_failed_yardsticks.py`, with probes `bscore.py` and `pairscore.py`.
- **Unscored Voynich census (different definition: pieces ≥ 1 character, pieces ≥ 10 uses):**
  - of 4,005 once-only words, 31% cut into two common words;
  - line-last 37% vs middle 32% vs first 25%; paragraph-first lines 21%;
  - by section: bathing 47% (expected 31% from length), herbal 27%, stars 32%;
  - per-scribe own-vocabulary rates: scribes 1–3 give 37–39%;
  - re-spacing all splittable rare words changes 150-word richness from 111.9 to 109.1.
- **Smoke run (2 generator stretches, latVUC, ita1885; no Voynich):**
  - Part A: unplanted D −0.008 to +0.003; planted +0.10 to +0.14.
  - Part B: unplanted Z −1.26 to +2.11 (ita1885 +2.11 > 2: natural content differences between sections can exceed
    2 in a real language); planted Z +4.3 to +19.8.
  - Part B was redesigned after a first smoke run in which a version using 2,500-token subsamples failed its generator
    known answer (planted Z −2.3, −0.8).
