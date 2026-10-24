# E055 pre-registration (picture route): do drawings with the SAME label look like the same plant?

Written 2026-10-24, before any pair image is built or rated. Script: `experiments/e055_same_label_pairs.py`. Updates
`reports/LEDGER.md`.

## Question
In the pharmaceutical section (DEV folios f88r, f88v, f89r1, f89r2, f89v1, f89v2, f99r, f99v, f100r, f100v and
f101v; the locked f102 leaves are excluded), small plant drawings carry short labels. Some labels recur on different
drawings: okol and otoldy three times each; otoky, otaly, otor, okaiin, oky and dar twice each. That gives 12
same-label pairs.

- **If labels are names of plants,** drawings sharing a label should look alike.
- **If labels are invented with no reference to the drawing,** same-label pairs should look no more alike than any
  two drawings from the same pages.

This needs no language guess.

## Data and the label-to-drawing maps (disclosed)
- **Images:** Yale Beinecke MS 408, IIIF.
- **Maps:** each label's position and its drawing were mapped by vision sub-agents, with a confidence level per
  label (files `scratchpad/beinecke/map_*.json`). In crowded areas the mapping is uncertain.
  - Of 207 labels, 178 plant labels were located.
  - **All located plant labels are used for the primary test.** The subset where both drawings are rated medium or
    high is reported as a secondary result.
- **Locked page incident:** while preparing f101v, an image of the LOCKED leaf f102r was displayed once (see LEDGER).
  It is not used anywhere.

## Pairs
- **Same-label pairs:** every pair of located plant drawings with an identical label (12).
- **Control pairs:** 4 per same-label pair (48). Each takes one drawing from each of the same two folios, or two from
  the same folio for a same-folio pair. Their labels are different, and not within one glyph of each other. Seed
  55055.
- **Identity pairs:** 6, each being one drawing cropped twice (different margin, slightly resized). These check that
  the judges are paying attention.
- **Masking:** in every crop, all mapped label positions on that image are blanked with paper-coloured boxes, so the
  judges compare drawings, not writing.
- **Order:** pairs are shuffled and named P01, P02 and so on. The key is kept in a separate file and read only after
  scoring.

## Judges
Two independent vision sub-agents (fresh context, no information about labels or this project), with the same
instruction:

> Each image shows two plant drawings side by side from a 15th-century manuscript (any writing has been blanked
> out). For each image, rate from 0 to 10 how likely it is that the two drawings depict the SAME kind of plant
> (same species), judging by root shape, leaf shape and arrangement, colour and overall structure (0 = clearly
> different plants, 10 = clearly the same plant). Use the whole scale. Return JSON {"P01": score, ...}.

- **A judge is VALID** if its mean identity-pair score is at least 8 **and** at least 3 points above its mean
  control score.
- **A pair's score** is the mean of the two judges.

## Decision
- **Statistic:** the mean same-label score minus the mean control score. The p-value is one-sided, from 20,000
  permutations of pair types.

| Outcome | Rule | Factor |
|---|---|---|
| VOID | either judge invalid | none |
| SAME LABEL = SAME-LOOKING PLANT | p < 0.01 **and** difference ≥ 1.5 points | M × 1/3 (labels refer to drawn objects) |
| NOT SHOWN | otherwise | none (only 12 pairs; a negative result is low-powered and is not scored) |

**Why the factor is only ×1/3.** A hoaxer who deliberately reused invented names for similar-looking drawings would
also pass. That would still mean the labels *name things*, but it would not prove a language.

## What was seen before writing this (disclosed)
- The maps, and which labels repeat.
- The f88r overlay, viewed while checking the pilot.
- No pair image has been built, and no drawing has been compared for similarity by anyone.
