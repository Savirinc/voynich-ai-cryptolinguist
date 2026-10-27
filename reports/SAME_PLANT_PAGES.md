# E085: do herbal pages showing the same plant share words? NO LINK (M × 1.4)

Run 2026-10-27 under `E085_PREREG.md` (locked). Script `experiments/e085_same_plant_pages.py`; results
`experiments/results/e085.json`, log `e085_run.log`. Arham's road 1 (picture cribs), bridge test.

## Known answer: Culpeper passes
328 herb entries, 47 pairs about the same kind of plant (the Agrimonies, Cresses, Thistles, Mustards...): vocabulary
overlap 0.0740 vs 0.0511 for random pairs (+45%), p 0.0001. In a real herbal, pages about the same plant share words.
VALID.

## Voynich
22 pairs of DEV herbal pages (different sheets) assigned the same plant by the early identifications, 12 plants:
| | same-plant pairs | matched random pairs | p |
|---|---|---|---|
| vocabulary overlap | 0.0137 | 0.0144 | 0.61 |
| identical first word | 0 of 22 | 0.000 | 1.00 |
Per plant: the highest overlaps are thistle f15r–f54r (0.045), henbane f31r–f48r (0.036), primula f39v–f40r (0.028);
five pairs share nothing beyond common words. No same-plant pair shares its first word.

**Verdict: NO LINK.** Ledger, as pre-registered: **M × 1.4.**

## Reading
- Pages that the early botanists judged to show the same plant do not share vocabulary, while Culpeper's same-plant
  entries clearly do. Either the identifications are mostly wrong, or the page texts are not about the plants drawn
  (or both).
- The "first word names the plant" crib has no support here: no same-plant pair shares a first word.
- The crib road with these identifications is closed. A better identification list (Tucker & Janick 2019; Sherwood)
  could reopen it; it would need a new pre-registration.
