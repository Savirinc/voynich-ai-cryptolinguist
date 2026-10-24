# E056: are the zodiac nymph labels numbers? — NOT NUMBERS (in ring order from a common start)

Pre-registration `reports/E056_PREREG.md` (sha b03c3e93…51a0, commit 71086cc). Script
`experiments/e056_zodiac_numbers.py`. Results: `experiments/results/e056.json`, `e056_run.log`.

| | Same word at the same ring position across months | p | Distinct words / labels |
|---|---|---|---|
| **Voynich zodiac labels** (12 pages, 292 labels) | **0.07%** | 0.91 | **245 / 292 (0.84)** |
| Planted numbers (with noise) | 48% | 0.0001 | 0.38 |
| Labels shuffled across pages | 0.15% | 0.75 | — |

**Verdict (pre-registered): NOT NUMBERS.** NUMBERS × 1/10, so 0.20 → **0.024**.
- The test easily finds a planted numbering, even with 32% noise.
- The real labels show no positional match at all (0.07%, below chance), and they are almost all different words.
  Covering 80% of label tokens needs 187 different words.

**Scope:** this excludes numbering *in the same ring order from the same starting point*. A rotated starting point,
or numbering that continues across the split Aries and Taurus pages, is not tested.

## What the labels look like instead
They are mostly unique words, as names would be (one per figure). They are built from a small kit of parts:
- **beginnings:** ot-, ok-, o-;
- **middles and endings:** -al, -aly, -ar, -eey, -ody, -aiin.

The commonest are otaly (6), otal, oky, otar, okeey, okal and okaly (4 each). They look like *variations on a few
patterns*, as a naming system or a set of similar-sounding names might be, or as invented words would be. Numbers they
are not.
