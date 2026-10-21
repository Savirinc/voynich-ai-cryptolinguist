# E035b: E035 rerun with 10 new seed pairs — NOT REPLICATED

Pre-registration: `reports/E035B_PREREG.md` (sha256 a5f90b24…0af9, locked before the run, commit d1b2e95). Script
`experiments/e035b_seed_replicates.py`. Results: `experiments/results/e035b.json`, `e035b_run.log`.

## Plain-language result
E035's match was luck of the draw. The same procedure, run with 10 fresh random seeds, matched only **1 time in 10**.
In the other 9 runs, Indonesian with spelling variation failed 2 or 3 features:
- **words seen once:** failed in all 10 runs (z +5.3 to +7.3);
- **persistence (PERS_30):** failed in 8 of 10 (z −2.84 to −3.57; E035's −2.98 was at the lucky end);
- **COV_30:** failed in 4 of 10.

By the pre-registered rule (2 or fewer matches): **NOT REPLICATED**. E035 is withdrawn, so L × 1/10 and C × 1/3.

## What survives from E035, and what doesn't
- **Survives, and was stable in all 10 runs:** spelling variation on a language that doubles words reproduces the
  exact copies, the near-copies, the flat Zipf head and the topic clustering. Those features never failed for
  Indonesian. So the mechanism *does* explain the flat head (C11) and the near-copies. That part is a real
  observation, but it isn't scored.
- **Doesn't survive:** "it matches Voynich". Two gaps are systematic, not noise:
  1. Voynich has **more words seen only once** (68% vs about 58%);
  2. Voynich's words **persist less** across the text (PERS_30 0.26 vs about 0.49).
- Both gaps point the same way. Voynich's vocabulary is more scattered than "a real text whose common words have a
  few spellings". That fits either:
  - spellings invented far more freely, so that most variants are used only once;
  - or something other than variation.

  Neither is tested.

## Ledger
After the correction: **M 0.054, L 0.868, C 0.069, O 0.009**, which is back where it stood after E034.
