# Stage B development notes: word-level codebook attack (not pre-registered; feasibility probes)

Probes in experiments/dev/wordsub_*.py. Synthetic only: plaintext words replaced by secret code ids (a perfect
codebook, no variants, no line rules), attacked with a word-bigram KN model plus the E017 delta-scored annealer.
Metric: share of tokens of the 300 most frequent code types decoded correctly (they cover ~50% of tokens).

| Probe | Plaintext | LM training text | Key | True-key score | Found score | Token accuracy |
|---|---|---|---|---|---|---|
| 1 | la 24k | la ref, 70k words, V=2000 | many-to-one | −4.09 | −3.54 | 0.20 (truth unstable: SA from truth → 0.00 at −2.54) |
| 2 | la 24k | la ref, V=5000 | one-to-one | −3.74 | −3.61 | 0.21 |
| 3 | la 12k | la ref + rest of tune (86k) | one-to-one | −3.94 | −3.68 | 0.29 |
| 3b | la 12k | la ref only (70k) | one-to-one | −3.93 | −3.72 | 0.16 |
| 4 | en 12k | other en books, 80k | one-to-one | −3.98 | −3.83 | 0.55 |
| 4b | en 12k | other en books, 168k | one-to-one | −3.89 | −3.76 | 0.47 |

## What this shows
1. **A many-to-one word key is ill-posed.** Many code types collapse onto a few frequent word pairs, and the LM
   rewards it. A codebook attack must cap the homophones per plaintext word.
2. **In every probe the true key scores worse than wrong keys,** so the objective, not the search, is the limit.
   The word models are trained on 70k–170k words (2–5 books); a bigram model over 5,000 words needs millions.
   More in-domain text raised accuracy (0.16 → 0.29); English (less inflection) reaches about 0.5.
3. Inflection hurts. Latin spreads one lemma over many word forms, so each form is rarer. That is exactly where
   the compound idea (stem + ending as separate units) could help, by decoding stems and endings separately.

## Needed before a pre-registered Stage B known-answer test
- Large word corpora per candidate language (millions of words; period-appropriate where possible): an
  acquisition job (e.g. Project Gutenberg Latin/Italian collections, Corpus Corporum, Biblioteca Italiana).
- A compound (stem + ending) attack variant.
- Homophone caps and a line model, then E017-style restarts plus agreement and long-word checks.

## Probes with a large open Latin corpus (2026-10-18)
External LM text: CLTK Latin Library (github.com/cltk/lat_text_latin_library, cloned, not vendored), 2,141 files,
13.66M words. 17 files sharing ≥ 3 eight-word passages with any la tune/test book were dropped (e.g. bible/daniel,
caesar/gall2), leaving 13.05M words. The file list is in the scratchpad (latlib_keep.json).

| Probe | Symbols | Search | True-key score | Found score | Token accuracy (top 300) |
|---|---|---|---|---|---|
| 5 | top 300 + one rare bucket | SA 3M | −3.36 | −3.40 / −3.41 | 0.45 / 0.35 |
| 5b | same | SA from truth | — | −2.70 (bucket mismatch exploited) | 0.07 |
| 6 | all 2,444 repeated types | SA 3M | **−4.73** | −5.70 to −5.86 | 0.14–0.20 |
| 6b | same | rank-local SA 3M–10M | −4.73 | −5.53 to −5.64 | 0.31–0.40 |
| 7 | same | best-response sweeps (ICM) | −4.73 | −5.81 | 0.19 |
| 7b | same | rank-local SA + ICM polish | −4.73 | −5.52 to −5.58 | 0.25–0.35 |

## What changed
1. **With a 13M-word model the yardstick is right:** the true key scores far above anything the search finds
   (−4.73 vs ≥ −5.52 per word pair). The problem is search again, as it was for letters in E016.
2. The lumped "rare bucket" design is unsound: rare code types must be kept as their own symbols (probe 5b).
3. The best search so far (rank-local proposals: a code word's candidate meanings are words of similar frequency)
   reaches 31–40% on the top types, which together are about half the tokens. That is still far below the true key,
   so the search is nowhere near done.

## Next ideas (not yet tried)
- Bayesian (Gibbs or slice-sampling) decipherment as in Dou & Knight 2012 for large word-substitution ciphers, with
  many restarts and the E017 agreement check.
- Exploit structure: decode endings (few, frequent, grammatical) first, then stems with endings fixed (compound
  hypothesis); match with Latin morphology.
- Seed with the most frequent function words (anchors) and grow outward.

## Compound (stem + ending) probes: endings first, then stems (2026-10-18)
Hypothesis class: each Latin word is split into stem + inflectional ending (fixed suffix list, longest match, stem
≥ 3 letters, words < 4 letters unsplit; `experiments/dev/latseg.py`). Stems and endings are each replaced by secret
codes. A missing ending stays visible. Plaintext: 24,000 words of la tune text. Reference statistics come from the
Latin Library (13.05M words). **Limitation:** the cipher and the LM use the same splitter, so segmentation is
known. On Voynich it would have to be inferred.

**Stage 1, endings only** (`endfirst.py`; 93 ending codes). Score = ending frequencies + ending bigrams of adjacent
words + *paradigm pairs* (pairs of endings seen on the same stem; Kober's triplet idea).

| Signals | Text | Ending token accuracy | Restart agreement |
|---|---|---|---|
| frequency + bigram + paradigm | 24k words | **0.988** | 0.993 |
| frequency + bigram (no paradigm) | 24k words | 0.936 | 0.963 |
| frequency + bigram + paradigm | 6k words | 0.862 | 0.933 |

**Stage 2, stems with decoded endings** (`stemsecond.py`, `ctxassign.py`). 2,052 code stems seen ≥ 2 times (91% of
tokens); 6,000-stem LM vocabulary (true stem inside for 93.8% of those tokens). Score = stem-bigram KN LM + a
per-stem Poisson likelihood of its decoded ending counts (frequency + paradigm). Init = one Hungarian assignment
on that likelihood. Then SA with candidate-restricted proposals, then iterated *context assignment* (all stems
re-assigned at once given their neighbours, then SA polish).

| Step (full pipeline, endings decoded in stage 1) | Stem accuracy (tokens) | Whole-word token accuracy |
|---|---|---|
| Hungarian init (no context) | 0.43 | 0.39 |
| + SA 10M | 0.56 | 0.51 |
| + iterated context assignment | **0.58** | **0.53** |

Stems decoded correctly, by how often they occur:

| Times seen | Stems | Share of tokens | Share correct |
|---|---|---|---|
| ≥ 100 | 24 | 0.26 | 0.83 |
| 20–99 | 189 | 0.29 | 0.64 |
| 5–19 | 593 | 0.22 | 0.32 |
| 3–4 | 565 | 0.08 | 0.12 |
| 2 | 681 | 0.06 | 0.05 |

Under the true key the stem bigram still scores better than the found keys (−5.76 vs −6.08 per word pair), so this is
still partly search-limited. Rare stems are also limited by the evidence itself.

## What this shows
1. **If Voynich words are built as stem + ending, the endings are the soft spot:** they can be read almost
   perfectly from frequency, word order and which endings share a stem, with no stem known.
2. Word-level reading improves from 31–40% (whole-word codes, top 300 types only) to 53% of *all* tokens.
   Frequent words are mostly right, rare ones mostly wrong: a skeleton reading, not a full one.
3. **Next:**
   - a full-word bigram (stem + ending) context in the assignment step;
   - restarts plus the E017 agreement and long-word checks;
   - then the step that matters for Voynich: *infer* the stem/ending split from the cipher itself.

   After that comes a pre-registered known-answer test with meaningless controls.

## Learning the stem/ending split from the cipher itself (2026-10-19)
Cipher words are now written as code stem + code ending glued together, with no separator (stems 2–5 glyphs,
endings 1–3 glyphs, 20-glyph alphabet). The attack must find the split itself.

Two code designs:
- **random**: endings use the same glyphs as stems;
- **marked**: endings use their own 6 glyphs, the way Voynich has typical word-final glyphs.

Scripts: `experiments/dev/segment.py`, `seg_gibbs.py`, `seg_oracle.py`, `seg_diag.py`.

| Segmenter | Code | Split correct (tokens) | Ending types found (true 93) | Endings decoded afterwards |
|---|---|---|---|---|
| Hard-EM, type counts | random | 0.40 (collapses to "no endings") | 0 | — |
| Gibbs, fixed glyph prior | random / marked | 0.62 / 0.67 | 200–500 | 0.29–0.50 |
| Oracle: true ending list, best rule | random | 0.74 (ceiling: endings blend into stems) | 93 | — |
| **Gibbs, glyph statistics learned separately for stems and endings, start from "no splits"** | **marked** | **0.995** | **93** | **0.983** (agreement 0.99) |
| same | random | 0.73 | 98 | 0.32 (agreement 0.74: correctly flagged as a failure) |

Diagnosis on the way: with a fixed glyph prior the model gives a *wrong* split a higher probability than the truth
(−139.7k vs −141.3k). Its main error is chopping words that have no ending (28% of tokens), so that version was
objective-limited. Learning which glyphs endings are made of fixes the objective. Starting from "no splits" stops
the ending lexicon from filling up with stem glyphs.

## What this shows
1. If a stem + ending notation writes endings recognisably (as any usable notation must, and as Voynich's
   word-final glyphs suggest), the split, the ending inventory and the endings' meanings can all be recovered from
   the cipher alone: 99.5% / 93 of 93 / 98.3%.
2. If endings are written in random glyphs, even the true ending list allows only 74% correct splits. The attack
   then fails, and the agreement statistic signals it.
3. Next:
   - **On twins:** run the stem stage on the inferred split, add the agreement and long-word claim rule, then a line
     model.
   - **On Voynich (a Stage A-style statistic, to be pre-registered):** does the segmenter find a compact ending
     inventory with its own glyphs on Voynich DEV, compared with twins of each family?

---

## Compound attack at Voynich's ending profile (2026-10-19, dev, no Voynich)

E026 found that Voynich has about 28 ending classes covering 95% of suffixed words, only partly written with their
own glyphs (DIST 0.39). This probe rebuilds the known-answer cipher at that profile and runs the full pipeline:
learned split → endings → stems. Scripts: `experiments/dev/cmp_pipe.py`, `holdout.py`, `calib.sh`; raw rows in
`experiments/dev/cmp_calib.jsonl`.

**Generator.** Latin word → stem + ending class, where class = the last two letters of the Latin ending. This is an
abbreviated ending system with 35 classes, 22 of which cover 95%. Codes use the 20 EVA letters. Ending glyphs are
drawn from their own 6 letters with probability 1 − α, else from all 20; stems likewise from the other 14. With
α = 0.6 the segmenter measures NSUF95 26 and DIST 0.39, which matches Voynich.

**Held-out plaintext.** The Latin "tune" text (28k words) was the only plaintext in every earlier Stage B probe. We
now hold out whole Latin Library files and remove them from the language model:
- CALIB, 6 files: Justinian codex 5 and digest 48, Fronto, Bacon, Gregory's decretals 1 and 3;
- TEST, 10 files, reserved for a future locked test (`holdout_files.json`).

**Claim signals tried.**
- *agf*: restart agreement on stems seen ≥ 20 times.
- *gap*: self-null, the attack's score per word minus its score on the same words in shuffled order.
- *pc*: pair-cover, the share of decoded (stem, class) pairs seen ≥ 5 times in Latin.

| Text | Split | Classes decoded | Stems | Whole words | agf | gap | pc |
|---|---|---|---|---|---|---|---|
| Latin "tune" text (seed 1, dev text) | 0.91 | 0.88 | 0.43 | 0.43 | 0.84 | 0.43 | 0.99 |
| Held-out Latin, 3 files | 0.83–0.87 | 0.68–0.79 | **0.11–0.20** | **0.10–0.19** | 0.65–0.70 | 0.16–0.19 | 0.98–0.99 |
| Stem-shuffled Latin (meaningless), 4 | 0.96–0.99 | — | 0 | 0 | 0.86–0.90 | −0.005–0.004 | 0.78–0.80 |
| Rugg grille (Voynich glyphs), 4 | — | — | — | — | 0.61–0.68 | **0.13–0.25** | 0.96–0.97 |
| Self-citation (Voynich glyphs), 4 | — | — | — | — | 0.58–0.61 | −0.02–0.10 | 0.88–0.93 |

## What this shows
1. **The earlier Stage B numbers were optimistic.** On the tune text they had been tuned on, stems were 43–58%
   correct. On unseen Latin they fall to 11–20%. Every future Stage B figure will be reported on held-out text.
2. **At Voynich's profile the split and the endings still come out:** split 83–87%, classes 68–79%.
3. **No claim signal separates a real crack from Rugg gibberish.** Rugg's small, repetitive vocabulary maps onto
   common Latin words. That gives it a better score than real Latin, a self-null gap as large (0.13–0.25 vs
   0.16–0.19) and nearly the same pair-cover. Agreement is about 0.6–0.7 everywhere.
4. Running a pre-registered known-answer test now would only confirm that the claim rule fails, so **E027 is not
   pre-registered yet.** Two things are needed first:
   - a stronger stem stage on held-out text;
   - a claim signal that Rugg-style repetition cannot fake. Candidates: predicting held-out lines from a key fitted
     on the other half, and a self-null that keeps the vocabulary size and repetition but breaks the meaning.
