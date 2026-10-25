# E061 pre-registration (campaign step 1): stems versus padding. Is the message in the stems?

Written 2026-10-25, before the run. Script: `experiments/e061_stem_stream.py`. Output: `experiments/results/e061.json`,
`e061_run.log`, report `reports/STEM_STREAM.md`. Updates `LEDGER.md`.

## Question
C14 says Voynich endings combine almost freely with stems: about 10 endings per stem, and the stem barely decides
the ending (I_EXCESS 0.32), unlike Latin, Indonesian, Malay and Swahili. One explanation is a **padding cipher**: the
stem carries the message (a letter or two, or a code), and the ending is a null, a filler or a check sign chosen
without regard to the stem. If so, stripping the endings should leave a stream of a few hundred stems that behaves
like a letter or syllable stream, far from any language's stem stream. If the endings are grammar, stripping them
should leave something that still looks like a language's stems.

**Terms.** The *stem* is the word with its ending removed. A *padding cipher* is a cipher where part of every written
word carries no information. *Collapse* is how much the number of distinct forms falls when endings are removed.

## Data
- **Voynich:** DEV prose clean tokens (28,841), word types with counts.
- **Languages (22):** Bible texts on disk, one window of 28,841 tokens each starting at token 10,000 (to skip opening
  genealogies and lists), normalised as in E042 (lowercase, diacritics removed): latVUC, eng-kjv, indayt, zlmKSZI,
  tglulb, cebulb, swhulb, yor, hausa, haw1868, ton, mri2012, hboWLC, turytc, ces1613, deu1912, ita1885, fraLSG, hun,
  grcbyz, arb-vd, tam2017.
- **Held-out word-like control:** Latin Library Caesar (`latin_library_e043/caesar`), first 28,841 tokens.
- **Generator (10):** Timm & Schinner, shipped configuration, seeds 31–40, 28,841 tokens each.
- **Padding-cipher controls (10):** built from latVUC, deu1912, ita1885, hboWLC, turytc (2 seeds each). The window's
  letters are cut into units of one or two letters (each cut 50/50, as in Naibbe). Each distinct unit gets a fixed
  code: a string of 2–4 EVA glyphs drawn from Voynich's glyph frequencies, unique per unit. Each code is followed by
  an ending drawn from E026's Voynich ending shares (none 0.19, y 0.18, dy 0.10, ol 0.06, aiin 0.05, edy 0.05, ar
  0.04, or 0.04, al 0.04, ey 0.03, ain 0.03, in 0.03, o 0.02, s 0.01, am 0.01; renormalised), independent of the
  code. Words = code + ending, 28,841 tokens.

## Procedure
Every text gets the same treatment. The unsupervised stem + suffix segmenter of E026 (`vcl.solvers.segment.
segment_types`, E026's settings: max_suf 4, min_stem 2, 120 sweeps, seed 61061) splits each word type; the stem stream
is the token stream with every word replaced by its stem. Four decision measures on the stem stream:

| Measure | Meaning |
|---|---|
| NSTEM95 | number of distinct stems that cover 95% of tokens |
| COLLAPSE | distinct stems / distinct words |
| STEM_HAPAX | share of stem types seen once |
| STEM_ZIPF | Zipf slope over the 100 commonest stems |

Reported, not decisive: the same four on the word stream, stem glyph predictability (h2 inside stems), SPLIT and NSUF95
from E026, and the generator's values.

**z-scores.** For each measure, z against the 22 languages (mean, sd with floor 2% of the value) and z against the 10
padding controls.

| Verdict | Rule |
|---|---|
| **PADDING-LIKE** | all 4 measures within 3 sd of the padding controls **and** at least 3 of 4 beyond 3 sd of the languages |
| **WORD-LIKE** | at least 3 of 4 within 3 sd of the languages (and not PADDING-LIKE) |
| GENERATOR-LIKE | neither, and all 4 within 3 sd of the generator samples |
| MIXED | otherwise |

## Controls (either failing makes the test VOID)
- Each padding control, scored leave-one-out against the other 9 and against the languages, must be PADDING-LIKE in
  at least 8 of 10 cases.
- Caesar (held-out Latin prose) must be WORD-LIKE.

## Ledger
| Outcome | Factor | Why |
|---|---|---|
| PADDING-LIKE | **C × 3** | a cipher class predicted it and nothing else does; the attack in step 3 is then built on stems |
| WORD-LIKE | **C × 0.8** (absence rule: padding form s = 0.25 of C, m = 0.2) | the padding form was searched by its own prediction and not found |
| GENERATOR-LIKE | none; recorded as a lean towards M | the generator reproduces Voynich surface forms, so matching it is weak evidence |
| MIXED / VOID | none | |

## Seed rule
Any decision z within 0.5 of the 3-sd bar is re-run with 10 segmenter seeds; the verdict stands only if ≥ 8 of 10 agree.

## Disclosed
- E026's ending shares and NSUF95 = 28 (used to build the controls); C14; E059's results.
- Nothing has been segmented or counted on stem streams for Voynich, the languages or the generator.
- The script's functions will be exercised on fabricated text before locking (disclosed here; no Voynich statistic).
- One attempt only (standing rule 9): no v2 unless a control fails for a reason that is a bug.
