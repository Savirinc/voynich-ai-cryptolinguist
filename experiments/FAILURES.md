# Negative and void results (protocol v1 section 5)

## E002 (2026-10-15): structure models, posterior predictive checks
- P5 (label ot/ok/op/of-initial share >= 0.55) FAILED for every frozen generator (KN4+variety 0.12, TF d160+variety 0.13),
  vs DEV and vs LOCKED_TEST. The models are prose-only. DEV labels themselves sit at about 0.41.
- P1 and P2 FAILED vs DEV for the best-predicting model (TF d160+variety): it exaggerates y->q (OR 6.68 vs CI [4.09, 5.72])
  and line-final m/iin (OR 30.3 vs CI [12.2, 29.7]). Both passed vs LOCKED_TEST because that CI is wide (15 leaves).
- The masked-objective Transformer head was not implemented (optional in the brief).
See experiments/results/e002_ppc.json and reports/STRUCTURAL_FINDINGS.md.
