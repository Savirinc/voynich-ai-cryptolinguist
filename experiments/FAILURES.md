# Negative and void results (protocol v1 section 5)

## E002 (2026-10-15): structure models, posterior predictive checks
- P5 (label ot/ok/op/of-initial share >= 0.55) FAILED for every frozen generator (KN4+variety 0.12, TF d160+variety 0.13),
  vs DEV and vs LOCKED_TEST. The models are prose-only. DEV labels themselves sit at about 0.41.
- P1 and P2 FAILED vs DEV for the best-predicting model (TF d160+variety): it exaggerates y->q (OR 6.68 vs CI [4.09, 5.72])
  and line-final m/iin (OR 30.3 vs CI [12.2, 29.7]). Both passed vs LOCKED_TEST because that CI is wide (15 leaves).
- The masked-objective Transformer head was not implemented (optional in the brief).
See experiments/results/e002_ppc.json and reports/STRUCTURAL_FINDINGS.md.

## E003 (2026-10-15): classical solver solver-v1 on known-answer benchmark v1 (checkpoint sha256 690ab0a5...)
Single frozen run; no change was made after test results were seen (no protocol deviation). A 2-task-per-split
pipeline smoke run (`--limit 2`, 14 test tasks) was executed before the full run to check the script; its outputs
were deleted and nothing was changed afterwards.
- Gate 1 PARTIAL -> every train family is VOID for Voynich use: test_in mean char acc mono 0.83, homophonic 0.82,
  nulls 0.70, vigenere 0.65, columnar 0.52 (threshold 0.90). Failures concentrate at 300-char plaintexts
  (vigenere 0/6 solved, columnar 2/12) and in wrong language selection.
- Gate 2 FAIL for held-out encodings: test_enc char acc 0.063 (ratio 0.09; only boundary_noise partly solved, 8/140),
  test_both 0.111 (ratio 0.16). Family-ID accuracy is 0 by construction (held-out labels are never predicted).
- Gate 2 FAIL for 'language not in library' (R2, train-family LMs only): test_lang 0/120 solved, test_both 0/140.
  (R1 test_lang PASSES, ratio 0.97, because every test language has its own ref-book LM in the R1 library.)
- Gate 3 FAIL: decoy false-discovery rate 0.0625 (5/80) > 0.05; all 5 are `markov` decoys (5/13 = 0.38): order-2
  resamples of real ciphertext decode to locally fluent text that the calibrated confidence accepts
  (confidences 0.63-0.99). autocopy, grille, zipf_bag, one_time_pad, short_mono: 0 false discoveries.
See experiments/results/e003.json and e003_rows.jsonl.
