# E104 (Arham, Reddit idea R13): do Voynich word pairs occur in both orders?

- **Pre-registration:** `E104_PREREG.md` (sha256 4637e12b…), commit 16df2d2.
- **Script:** `experiments/e104_pair_reversal.py`.
- **Results:** `experiments/results/e104.json`, log `e104_run.log`. Run 2026-10-31, 41 s.

## Verdict (pre-registered): GENERATOR-LIKE, M × 3
ASYM is how strongly a recurring word pair keeps one order (A B rather than B A), beyond what a coin would give: 0
means order-free, 1 means fully fixed.

| Group | ASYM p10–p90 (range) | Pairs seen in both orders (REV) |
|---|---|---|
| 69 meaningful texts | 0.544–0.672 (0.428 Danish to 0.703 Tamil) | 0.08–0.60 |
| 60 copy-generator stretches | 0.101–0.519 (E032 default 0.115–0.177) | |
| **Voynich** | **0.179** (sd 0.021; 232 pairs) | **0.89** |

VALID (0.519 < 0.544). The Voynich is far inside the generator band and 12 sd below the lowest meaningful text. No
seed check was needed.
- **Its most reversible pairs** occur equally often in both orders: *chey qokain*, *ar or*, *otedy qokedy*,
  *daiin dain*, *chedy lchedy*, *ain ar*, *cthol daiin*.
- **Fincher's observation holds:** 89% of recurring Voynich pairs are seen in both orders.

## Robustness (unscored, after the run)
- **Not just near-copies.** Removing pairs whose two words differ by ≤ 2 or ≤ 3 letters leaves the Voynich at 0.191
  (169 and 135 pairs). Latin (0.59), Danish (0.46–0.49) and Lingala (0.56) stay put, and the generator falls to
  0.07–0.13. So this is not the near-copy fact (C21, E066) counted again.
- **Not explained by verse.** Latin poetry, whose word order is famously free, still keeps recurring pairs in order:
  Ovid 0.558, Vergil 0.582, Prudentius 0.596. Practical prose agrees: Apicius 0.554, Cato 0.642, Columella 0.543.
- **Caveat.** Some generator settings that choose source words at random reach 0.39–0.60, so a mechanical process can
  also produce fixed orders. The Voynich, however, matches the page-local copying settings (default 0.12–0.16,
  `err10_position` 0.09–0.20).

## What it means
In every meaningful text tested, prose or verse, a pair of words that recurs keeps its order. In the Voynich, recurring
pairs come in both orders almost as often as a coin toss would give. This is what a copy-and-vary process produces, and
it fits E048 (weak order information). It also fits "heavy nulls or transposition" (Fincher). E048's 7-sd result still
argues against a full within-line shuffle, but a cipher that reorders words remains open.

## Ledger
M × 3: **M 0.7422, L 0.1816, C 0.0342, O 0.0421.**
