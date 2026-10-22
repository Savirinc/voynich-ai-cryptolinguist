# E041 pre-registration: does Currier B fit the simple-syllable range when *qo* and *dy* are single signs?

Written 2026-10-22, before the run. Script: `experiments/e041_b_units.py`. Working assumption L. This is a
measurement, with no ledger factor.

## Question
E040: after cleaning (e-runs → e, t → k), Currier B is more predictable within words than any sampled
simple-syllable language (h2 2.04, floor 2.23).
- E027 had already found a fix of exactly this kind: reading the two most rigid glyph pairs, ***qo*** and ***dy***,
  as single signs (segmentation S3) raised h2.
- **Does B return to the natural range at S3?**

## Design
- **Data:** the cleaned inventory N1 (E040).
- **Texts:** Currier A, Currier B, and B in 10 runs of consecutive lines matching A's token count (seed 41041).
- **Segmentations:** S2, as in E040, and S3 = S2 + *qo*, *dy*, exactly E024's pre-existing definition. **No other
  grouping is tried.**
- **Measures:** h1, h2 and L (E024 code), against E027's simple-syllable range: h1 3.33–4.71, h2 2.23–2.88,
  L 2.74–4.21.

## Readings, fixed now
| Result | What step 2 does |
|---|---|
| **B (all lines) at S3 inside on all three** | A and B are the same kind of writing once *qo* and *dy* are single signs. Step 2 uses **both**, with B at S3. |
| **B at S3 still outside** | B is more rigid than any natural language sampled. Step 2 uses **A**, and B is reported separately. |

Also reported:
- **A at S3:** if A falls outside at S3, then S3 does not suit A, and each variety keeps its own best-fitting
  segmentation. That is stated as a limitation.
- **The B(A-size) share of runs inside.**

## What was seen before writing this (disclosed)
- E027's S3 results on raw DEV (inside).
- E040's S2 results on cleaned A and B.
