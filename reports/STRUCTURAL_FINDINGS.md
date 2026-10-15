# Structural findings: E002 (System A, Voynich-native structure models)

Protocol: `eval/PROTOCOL_v1.md` (Gate 4: structure only). **No decipherment.** Nothing below assigns meaning, a language, or a word class to any glyph, word or cluster.

## Event stream
- Source: ZL3b IVTFF. Prose lines only, clean tokens only (`[a-z]+`, no `?`), first alternative reading, uncertain spaces counted as word boundaries. Unclean tokens are dropped from their line.
- Each word is followed by exactly one end symbol: `_`, or `$` for the line-final word. Events = glyphs + words. The vocabulary is fixed at 28 symbols (a–z, `_`, `$`), with no OOV exclusions.
- bits/glyph = total bits / events. bits/word = total bits / words, which is the sum over each word's glyphs plus its end symbol.
- DEV has 85 leaves, 3,406 lines, 28,841 words and 172,791 events. Each line is one context and the line start is padded with `^`.

## Results (bits; lower is better)
DEV figures are 5-fold leaf-grouped CV, pooled over every DEV line, with each line scored once. LOCKED_TEST was scored once per frozen model, after retraining on all DEV leaves, and logged in `experiments/LEDGER.csv`.

| Model | Params | DEV CV bits/glyph (fold sd) | DEV CV bits/word | LOCKED_TEST bits/glyph | LOCKED_TEST bits/word |
|---|---|---|---|---|---|
| unigram (add-one) | 28 | 3.959 (0.011) | 23.72 | 3.971 | 23.75 |
| KN n=2 / +variety | – | 2.174 / 2.122 | 13.02 / 12.71 | – | – |
| KN n=3 / +variety | – | 1.916 / 1.873 | 11.48 / 11.22 | – | – |
| KN n=4 / +variety | – | 1.888 / **1.856** (0.077) | 11.31 / **11.12** | **1.921** | **11.49** |
| KN n=5 / +variety | – | 1.899 / 1.878 | 11.38 / 11.25 | – | – |
| KN n=6 / +variety | – | 1.932 / 1.917 | 11.58 / 11.49 | – | – |
| Transformer d96 L3 / +variety | 0.36M | 1.806 / 1.795 | 10.82 / 10.76 | – | – |
| Transformer d160 L4 / +variety | 1.28M | 1.811 / **1.788** (0.077) | 10.85 / **10.71** | **1.844** | **11.03** |
| Ablation: KN4 with uncertain spaces merged | – | 1.905 | 12.13* | – | – |

\* This ablation uses a different event stream with fewer words, so its bits/word is not comparable with the other rows.

- KN is interpolated modified Kneser–Ney. "+variety" mixes a Currier-A/B-specific KN with the pooled KN, with λ tuned on an inner split of the training leaves (λ=1.0 when frozen). For the Transformer, "+variety" adds Currier-variety and paragraph-first-line embeddings.
- Variety conditioning helped in every class: −0.03 to −0.05 bits/glyph for KN and −0.01 to −0.02 for the Transformer.
- KN performance peaks at n=4. Higher orders overfit about 29k words.
- Transformers beat the best KN by about 0.07 bits/glyph on DEV CV and on LOCKED_TEST.
- The Transformers are char-level and autoregressive, with line context and early stopping on inner-validation leaves taken from training leaves only. The masked objective was **not** implemented.
- LOCKED_TEST is about 0.03–0.06 bits/glyph harder than DEV CV for both KN and the Transformer. The ranking is unchanged.
- Frozen checkpoints and their sha256 are in `checkpoints/e002_frozen_*` and `experiments/results/e002.json`.

## Posterior predictive checks (P1–P6)
Samples come from the frozen models, drawn by ancestral sampling at T=1. There is one sampled line per DEV line template (variety and paragraph-start), and the templates are used twice. Thresholds are exactly as in the protocol. "DEV" compares with statistics of all DEV leaves, which are the frozen model's training leaves, so this is an in-sample distributional check. "LOCKED" compares with LOCKED_TEST statistics, computed once.

| Check | KN4+variety vs DEV | KN4+variety vs LOCKED | TF d160+variety vs DEV | TF d160+variety vs LOCKED |
|---|---|---|---|---|
| P1 y→q OR in held-out 95% CI | PASS (4.81 in [4.09, 5.72]) | PASS (in [3.05, 7.37]) | **FAIL** (6.68) | PASS |
| P2 line-final m/iin OR in CI | PASS (20.6 in [12.2, 29.7]) | PASS (in [9.8, 50.3]) | **FAIL** (30.3) | PASS |
| P3 q→o share within ±0.02 | PASS (0.978 vs 0.978) | PASS | PASS | PASS |
| P4 Currier A/B sign of P1 and P2 difference | PASS | PASS | PASS | PASS |
| P5 label ot/ok/op/of-initial share ≥ 0.55 | **FAIL** (0.12) | **FAIL** | **FAIL** (0.13) | **FAIL** |
| P6 TTR within ±10% at matched length | PASS (+7.2%) | PASS (+0.6%) | PASS (+0.5%) | PASS (−6.1%) |

- The content-free KN generator reproduces P1–P4 and P6. This shows that local glyph statistics alone are enough to produce the y→q, line-final m/iin, q→o and A/B effects.
- The better-predicting Transformer **exaggerates** the two context effects (y→q OR 6.7, m/iin OR 30.3) beyond the DEV CI. It passes against LOCKED_TEST only because that CI is wide: there are just 15 leaves. Better bits do not mean better reproduction of these statistics.
- P5 fails for every model. The models are trained on prose and never see labels, and P5 has an absolute threshold. For reference, the DEV labels themselves have an ot/ok/op/of-initial share of only 0.41 (LOCKED_TEST labels: 0.32). This is the statistic that failed before, and it has been kept exactly as written.
- PPCs are fixed thresholds, not p-values, so no Holm correction applies. Details are in `experiments/results/e002_ppc.json`.

## Caveats
- **Predictive fit is not semantics.** A lower bits/glyph or a passed PPC says the glyph stream has learnable local structure. It says nothing about meaning, language or decipherability.
- **Our numbers are not comparable to the external 11.01 bits/word figure.** Their scoring code and tokenisation are not available, and their split differs from ours (see `reports/MISSING_EXTERNAL.md`). The approximate comparison below does not change this.
- Transformer training on MPS is not guaranteed to be bit-reproducible. The checkpoint sha256 is the record of the frozen model.
- During data inspection, aggregate statistics (glyph counts, maximum line length, label share) were printed once over the full corpus, including LOCKED_TEST leaves, to size the vocabulary and context. No model or hyper-parameter was fitted on locked data.
- The Transformer sizes and the choice of n came from DEV CV only.

## E002b: approximate comparison with external round-2 split
**APPROXIMATE comparison: tokenisation and scoring conventions not verified identical; their code is not available.**

- **External blind set:** leaves 24, 72, 80 and all of quire E (leaves 33–40), 3,019 tokens in their corpus. Their best model was a char 5-gram conditioned on the previous unit's final glyph and on line-final position, at 11.01 bits/word on blind prose.
- **Locked-leaf exclusion:** quire E overlaps our LOCKED_TEST leaves 35 and 38. Both were excluded and never loaded here.
- **Our scored set:** 8 leaves with prose in our default stream (24, 33, 34, 36, 37, 39, 40, 80; leaf 72 has no prose lines). That is 2,257 clean words (2,272 prose tokens including unclean ones) and 12,905 events.
- **Training set:** all of our DEV leaves minus their blind leaves.

| Model | bits/word | bits/glyph |
|---|---|---|
| unigram | 22.86 | 3.997 |
| KN n=4 / n=5 | 10.97 / 10.99 | 1.918 / 1.922 |
| KN n=4 + variety | 10.72 | 1.875 |
| KN conditioned on previous-word final glyph + line-final flag, n=3 / 4 / 5 / 6 | 10.69 / **10.65** / 10.75 / 10.90 | 1.869 / 1.862 / 1.880 / 1.906 |

- Conditioning gains about 0.24–0.32 bits/word over plain KN of the same n. This matches the external replication (0.24–0.30).
- The absolute values are below 11.01, but they are **not** evidence of a better model:
  - The sets differ: 35 and 38 are missing, and only clean tokens are scored.
  - Word-end conventions may differ.
  - The line-final flag is side information that makes our end symbol nearly free.
  - These leaves are DEV leaves for us, so model-class and n choices were informed by CV that included them.
- Details are in `experiments/results/e002b.json`.

## E006 — Voynich fingerprint vs 18 known-answer mechanisms (structural hypothesis ranking)
Command: `.venv/bin/python experiments/e006_voynich_fingerprint.py` → `experiments/results/e006.json`.
Reference: 60 streams × 18 classes (13 encoders over 36 languages, raw plaintext, 4 nonlinguistic generators), each
3,000 symbols; Voynich: DEV leaves only, 57 windows (EVA characters) / 49 windows (fused multi-glyph units).

| Class | h1 | **h_cond (bits)** | glyph types | mean word len |
|---|---|---|---|---|
| **Voynich (EVA chars)** | 3.81 | **2.12** | 19 | 5.0 |
| **Voynich (fused units)** | 3.94 | **2.39** | 27 | 4.1 |
| plain / mono / reversed_words | 4.3 | 3.40–3.49 | 30–32 | 4.6–4.9 |
| abjad | 3.90 | 3.45 | 23 | 3.1 |
| homophonic / vigenere / autokey | 4.7–5.7 | 4.09–4.24 | 30–59 | 4.9–5.0 |
| verbose (1–3 glyphs per letter) | 3.12 | 2.57 | 10 | 8.5 |
| syllabary | 7.33 | 2.66 | 444 | 2.3 |
| decoy: grille (Rugg-style) | 4.14 | 2.71 | 20 | 5.4 |
| decoy: autocopy (Timm–Schinner) | 4.18 | 3.45 | 22 | 5.3 |

- **No mechanism in the library reproduces Voynich's conditional glyph entropy** (2.1–2.4 bits). Every linguistic
  class is ≥ 3.4. This independently reproduces the external R2 finding (h2 2.0–2.5 vs 3.1–3.4).
- The classes nearest on h_cond (verbose, syllabary, grille) are far off on other axes (types, word length).
- Positive control (grouped CV by source book): 13/18 classes identified at ≥ 0.83; plain/mono/reversed_words are
  mutually indistinguishable by construction (features are relabelling-invariant), markov decoys 0.53. Classifier
  "top class" outputs for Voynich are therefore weak evidence; the entropy gap is the robust observation.
- **Consequence for the curriculum (Milestone 3):** add generators that hit ~20 types, h_cond ≈ 2.1, word length ≈ 5
  (e.g. slot/positional grammars over syllable codes, verbose ciphers with positional glyph constraints) as both
  linguistic encodings and decoys, then re-test whether solvers can tell them apart. No semantic claim.
