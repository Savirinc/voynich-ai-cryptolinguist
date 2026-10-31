# E101 (Arham, Reddit R2 follow-up): where are the glued-looking words?

- **Pre-registration:** `E101_PREREG.md` (sha256 69cce2dd…), commit 7618b3f.
- **Script:** `experiments/e101_glue_where.py`.
- **Results:** `experiments/results/e101.json`, log `e101_run.log`. Run 2026-10-31, 11 s.
- **No Bayes factors (pre-registered).**

GLUED: a word of ≥ 4 characters, used ≤ 2 times, that cuts into two pieces of ≥ 2 characters, each a word used ≥ 2
times.

## Part A, line ends: SQUEEZE-LIKE (pre-registered verdict), but confounded (see caveat)
| Text | GLUED rate, line-last − middle (D) |
|---|---|
| 10 generator stretches | −0.008 to +0.009 |
| Same stretches, 15% of lines with last two words joined | p10 +0.103 |
| 5 languages | 0.000 to +0.003; planted +0.086 to +0.170 |
| **Voynich** | **+0.138** (line-last 23.8% vs middle 10.0%; sd 0.008) |

VALID. The Voynich is above every unplanted control and at the level of planted line-end joins. By section: herbal
+0.081, stars +0.134, bathing +0.097.

**Caveat (unscored, seen after the run):**
- Voynich line-end words are rarer in general (38% are rare vs 19% mid-line); the controls show no such effect.
- Their commonest second pieces are word endings: *-dy* (47), *-am* (39), *-dam*, *-om* (17 each), *-al*, *-ain*.
  19% of glued line-end words end in *-m*, against 2% mid-line.
- Counting rare words only, the glued share is 62% at line ends vs 54% mid-line: a much smaller gap.

So most of the excess matches the known line-end word forms (E059, E075: line-end *-m/-y* is a job of the pieces)
rather than plain squeezing. The two readings cannot be separated here: a scribe running out of room and adding a
compact ending looks the same in the text.

## Part B, bathing section: VOID
The generator false-positive check failed: 3 of 10 unplanted stretches gave Z > 2 (range −7.9 to +5.1). Section-level
rates vary too much even in homogeneous meaningless text. Planted joins were detected in 9/10.

Unscored: under this stricter definition, bathing has *fewer* glued-looking words (9.1%) than herbal (14.8%) and stars
(11.7%), Z −8.9. The census's bathing excess came from one-glyph pieces and very common words, so it is not a robust
section habit.

## What this adds
Rare words cut neatly into two real words, and this happens most at line ends. The line-end part is mostly the known
line-final word forms. No evidence ties gluing to one scribe or to the bathing section.

## Ledger
No change: M 0.4897, L 0.3594, C 0.0676, O 0.0833.
