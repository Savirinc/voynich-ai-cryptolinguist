# E102 (Arham, Reddit idea R1): does the vocabulary drift with position, beyond topic?

- **Pre-registration:** `E102_PREREG.md` (sha256 209e4ee3…), commit 5ae90fd.
- **Script:** `experiments/e102_drift.py`.
- **Results:** `experiments/results/e102.json`, log `e102_run.log`. Run 2026-10-31, 32 s.

## Verdict (pre-registered): VOID, no factor
DRIFT measures how much more vocabulary near pages share than far pages, within the same Currier language, scribe and
section, on different sheets. The pairs are 2,525 page pairs in 6 groups.

| Group | DRIFT, p10–p90 (range) |
|---|---|
| 69 meaningful texts | +0.238 to +0.411 (+0.19 to +0.48) |
| 60 copy-generator stretches | +0.203 to +0.423 (+0.09 to +0.51) |
| 5 Naibbe texts (unscored) | +0.199 to +0.314 |
| **Voynich** | **+0.397** (sd 0.060) |

The bands overlap almost completely, so the measure cannot separate language from copying. Naibbe is not flat either:
with this design it drifts as much as the others, because the plaintext's own drift carries through.

## Unscored observations (seen after the run)
- **The pooled number mixes groups.** Herbal A (2,070 of the 2,525 pairs) spans the longest distances. Group
  differences in similarity therefore leak into the pooled correlation, which weakens the pooled statistic.
- **Within each group:**

  | Group (pairs) | Voynich | Meaningful median (p10–p90) | Generator median (p10–p90) | Naibbe median |
  |---|---|---|---|---|
  | Herbal A, scribe 1 (2,070) | +0.28 | +0.11 (+0.01 to +0.26) | +0.19 (+0.02 to +0.28) | +0.04 |
  | Herbal B, scribe 2 (160) | +0.11 | +0.19 | +0.17 | +0.26 |
  | Bathing B, scribe 2 (114) | −0.03 | +0.14 (−0.08 to +0.48) | +0.01 (−0.19 to +0.16) | −0.08 |
  | Stars B, scribe 3 (129) | +0.04 | +0.23 (+0.06 to +0.43) | +0.00 (−0.13 to +0.11) | +0.02 |
  | Pharma A, scribe 1 (44) | −0.07 | +0.13 (−0.10 to +0.45) | +0.03 (−0.24 to +0.29) | −0.09 |

  In the three compact sections (bathing, stars, pharma), languages usually drift and the generator and Naibbe do not.
  The Voynich does not drift there. In herbal A the Voynich drifts strongly, at the top of both ranges. This pattern
  was found after the run and is unscored. A test of it would need its own pre-registration.
- **Reddit's "late small-plant pages" claim is not supported.** Pharma pages are slightly *more* similar to the far
  herbal A pages of the same scribe (0.325) than to their nearest pages from other groups (0.303).

## Ledger
No change: M 0.4897, L 0.3594, C 0.0676, O 0.0833.
