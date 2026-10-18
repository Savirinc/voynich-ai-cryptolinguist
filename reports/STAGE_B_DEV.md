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
