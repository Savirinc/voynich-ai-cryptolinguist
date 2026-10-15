# Evaluation Protocol v1 (LOCKED)

Locked 2026-10-15 before any model in `src/vcl/models`, `src/vcl/solvers` or `src/vcl/agents` was trained or run.
Its SHA-256 is recorded in `eval/PROTOCOL_v1.sha256` and checked by `tests/test_protocol_lock.py`.
Any change requires a new version file (`PROTOCOL_v2.md`) with a dated rationale. Results under v1 stay reported under v1.

## 1. Voynich data and splits
- Source: ZL3b IVTFF v3b (13/05/2025), `data/raw/handoff/source_dump/IVTFF Eva.txt.docx`, SHA-256 `6aedc059…ddb7`, parsed by `src/vcl/corpus/ivtff.py`.
- Grouping unit: **physical leaf** (folio number; recto and verso together). Bifolio grouping is a reported robustness check.
- **LOCKED_TEST leaves** (salt `vcl-protocol-v1-2026-10-15`, 15% per illustration section):
  `1, 8, 9, 30, 35, 38, 51, 52, 56, 75, 86, 87, 102, 105, 114` (6,004 prose tokens).
  These leaves are never read by development code. Each *frozen* model is scored on them once; the score and the
  model checkpoint hash go into `experiments/LEDGER.csv`. A second scoring of a modified model counts as a new
  model and both results are reported.
- DEV: remaining leaves in 5 salted-hash folds (`data/derived/splits.json`).
- Default token stream: prose, clean tokens (`[a-z]+`, no `?`), first alternative reading. Uncertain spaces (`,`)
  are treated as word boundaries in the default stream and are an explicit ablation.

## 2. Voynich structure metrics (Gate 4)
- Primary: held-out **bits per glyph** (EVA character incl. a word-end symbol) and **bits per word** = sum of glyph
  bits over the word plus its end symbol, so every model is scored on the same event stream. Unknown glyphs:
  vocabulary is fixed to EVA a–z plus boundary symbols; no OOV exclusions.
- Baselines that must be reported alongside: unigram, Kneser–Ney n-gram (n=2..6), and a content-free generator.
  The external 11.01 bits/word figure is NOT comparable unless its split and scoring are reproduced (it is not
  in this repository; see `reports/MISSING_EXTERNAL.md`).
- Posterior predictive checks (preregistered; directions and thresholds fixed here) on samples from a frozen model,
  compared with DEV and, once, LOCKED_TEST statistics:
  - P1 y→q odds ratio of samples within the leaf-bootstrap 95% CI of the held-out data.
  - P2 line-final m/iin odds ratio within the held-out CI.
  - P3 q→o share within ±0.02 of held-out.
  - P4 Currier A vs B: model conditioned on variety reproduces the sign of the A/B difference for P1 and P2.
  - P5 label ot/ok/op/of-initial share ≥ 0.55 (the previously failed statistic; retained as written).
  - P6 type/token ratio of samples within ±10% of held-out at matched length.

## 3. Synthetic known-answer benchmark (Gates 1–3)
- Every task stores: plaintext, encoder family + code version, secret key, source provenance (URL, licence,
  SHA-256), language, language family, seed, difficulty, ciphertext, and an identifiability tag
  (`unique` | `equivalence_class` | `non_identifiable`). Plaintext/key/verifier are visible only to `src/vcl/eval`.
- **Holdout axes** (each a separate test table, never pooled into one number):
  1. held-out *language family* (whole family absent from any solver/agent tuning),
  2. held-out *encoding family* (whole mechanism absent from tuning),
  3. held-out *source document*,
  4. both (1) and (2) together.
- Solvers and agents may be tuned only on the TRAIN families listed in `configs/benchmark_v1.yaml`.
- Metrics: character accuracy, word accuracy, exact-key recovery, encoding-family identification accuracy,
  **abstention** rate and **selective accuracy**, expected calibration error (10 bins), and false-discovery rate
  on decoys (claims of a solution where none exists).
- Correct answer for `non_identifiable` tasks and nonlinguistic decoys is to abstain / declare "no language".

## 4. Gates (enforced in `src/vcl/eval/gates.py`)
- **Gate 0** reproducibility: corpus hash, protocol hash, seeds, environment lock present; ledger row written.
- **Gate 1** positive control: before a solver is applied to Voynich it must reach ≥ 0.90 character accuracy on
  matched known-answer synthetic tasks of the same family. Otherwise the Voynich run is **VOID** (not negative).
- **Gate 2** OOD transfer: report per holdout axis; "generalises" requires held-out-family character accuracy
  ≥ 0.5 × in-family accuracy AND above the matched random-key baseline with p < 0.01 (binomial/permutation).
- **Gate 3** nonsense controls: decoy false-discovery rate ≤ 0.05 at the operating threshold.
- **Gate 4** Voynich structure: as section 2. No semantic claim at this gate.
- **Gate 5** semantic validation: requires a frozen productive mapping, original-order readings, two independent
  external semantic predictions made before checking, positive-control success and independent adversarial
  reproduction. Absent this, every report must say **"no decipherment"**.

## 5. Statistics
- Effect sizes with 95% leaf-cluster bootstrap CIs (2,000 resamples). Holm correction across the predeclared
  family of tests in any one experiment. All negative and void results go to `experiments/FAILURES.md`.

## 6. Leakage controls
- Pretrained-model agents are told only ciphertext and task metadata visible to a real decipherer.
- Plaintext sources for test families are chosen from texts unlikely to be memorised verbatim where possible
  (UDHR-style texts are flagged as *likely memorised*; results on them are reported separately).
- No retrieval of plaintext corpora by the agent during evaluation.
