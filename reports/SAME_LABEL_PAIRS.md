# E055 (picture route): do drawings with the same label look like the same plant? — NOT SHOWN (no difference at all)

Pre-registration `reports/E055_PREREG.md` (sha 720db7ca…db42d), amendment `E055_AMENDMENT.md` (mask size). Script
`experiments/e055_same_label_pairs_v2.py`. Results: `experiments/results/e055.json`, `e055_key.json`,
`e055_judgeA.json`, `e055_judgeB.json`. Maps: `experiments/results/e055_maps/`.

## Result
Scores are the mean of the two judges, from 0 (clearly different plants) to 10 (clearly the same plant).

| Pair type | n | Mean score |
|---|---|---|
| Identity checks (one drawing cropped twice) | 6 | **9.9** |
| **Same label** | 12 | **2.17** |
| Control (same pages, different labels) | 48 | **2.40** |

- **Both judges are VALID:** identity checks scored 9.5–10, far above the controls.
- **Same-label pairs minus controls = −0.23 (p = 0.70).** With only confident mappings (both drawings rated medium
  or high; 8 pairs): −0.02 (p = 0.52).
- **Verdict (pre-registered): NOT SHOWN, no factor.**

**Pair by pair:** okol 2.0, 1.0, 0.5; otoldy 3.0, 1.0, 1.0; otor 3.5; otaly 3.0; dar 4.0; okaiin 3.0; oky 3.0; otoky
1.0. **No same-label pair was rated as a likely match** (the highest was 4.0).

## Plain reading
1. **Drawings that share a label look no more alike than drawings that don't.** The judges were clearly able to
   recognise the same drawing (9.9), so the test could see similarity when it was there.
2. **Several repeated labels are common words of the running text,** not rare name-like words:
   - dar is the 17th commonest word, okaiin the 20th, oky the 72nd, okol the 87th.
   - Only otaly, otoldy and otoky are rare.
   - Even for the rare ones, the pairs scored low (1.0–3.0).
3. **Limits, which mean this does not exclude naming:**
   - Only 12 pairs.
   - The label-to-drawing maps are uncertain in crowded areas.
   - Many crops are fragments.
   - Labels might name a *preparation* or *part*, not the plant.

   But nothing here supports the idea that a pharmaceutical label is the name of the plant drawn next to it.
4. **Unscored context:** about half of the pharmaceutical labels (49%) also occur somewhere in the running text. The
   median label word occurs 0 times in the prose.

## Consequence for the "find the plant name" plan
The plan assumed that a label is the name of the plant beside it. On the repeats that can be checked, that assumption
gets no support. Before investing in herbal matching and name-guessing, the assumption itself should be tested
differently, for example: does each herbal page's *first word* behave like a unique name?
