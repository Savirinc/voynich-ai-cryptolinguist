# E096 (Route 2): do the zodiac figure labels follow the period degree tables?

Pre-registration `E096_PREREG.md` (sha256 2be41a1e…), script (sha256 faad3aa9…), tables
`reports/data/degree_tables.json` (sha256 1615d824…; Lilly 1647 pp. 116–118, from the Al-Biruni and Alcabitius
tradition). Results `experiments/results/e096.json`, log `e096_run.log`. Run 2026-10-29, 34 s.

## Verdict: NO LINK (max-T 0.08, p 0.86). No factor.

## Known answers first
| Check | Result | Needed |
|---|---|---|
| Planted gender labels (front piece shows class, 9 in 10 figures) | 10/10 at p ≤ 0.01 | ≥ 8/10 ✓ |
| Planted light labels | 10/10 | ✓ |
| Planted term labels | 10/10 | ✓ |
| False-claim control (real labels, tables rotated) | 0/20 claims | ≤ 1 ✓ |
| Descriptive: weaker plants (front 0.6; similarity clusters 0.8) | p 0.10–0.43; 0.005–0.055 | — |

## Voynich
For each column, D is the extra resemblance of same-class labels over different-class labels.

| Column | D, right tables | D, wrong tables: mean (sd) | z | p |
|---|---|---|---|---|
| Gender (M/F) | 0.569 | 0.571 (0.051) | −0.03 | 0.52 |
| Light (light/dark/smoky/void) | 0.676 | 0.671 (0.063) | +0.08 | 0.47 |
| Terms (ruling planet bands) | 0.448 | 0.462 (0.019) | −0.74 | 0.77 |

With every ring start and direction allowed, the right sign's table fits the labels no better than other signs' tables.

## What it means
- **The labels do not encode** the degree's gender, light or term in a strong systematic way: their spelling does not
  track these classes for 9 in 10 figures, as the planted test would have caught.
- **A weak or partial encoding** (6–8 in 10 figures) is not excluded, because the test is not powerful enough to see it.
- **Other tables are not tested:** Picatrix degree images and al-Biruni's variants.
- **Ledger unchanged:** NO LINK carries no factor by pre-registration. M 0.4631, L 0.3604, C 0.0978, O 0.0788.
