# E060: the ingredient link (do pharma labels recur in the recipes?) — VOID (power control failed)

Pre-registration `reports/E060_PREREG.md` (sha256 57a7846f…e98cf, commit f523eba). Script
`experiments/e060_ingredient_link.py` (sha256 63f838af…955e3). Results: `experiments/results/e060.json`,
`e060_run.log`. The first run stopped at the generator step because the generator directory was given as a relative
path on the command line (the generator runs in its own working directory); the run was repeated with an absolute
path, same locked script and seed, and gave identical Culpeper and Voynich numbers.

## Verdict (pre-registered rule): VOID. No ledger factor.
| Control | Rule | Result |
|---|---|---|
| Power (Culpeper plant names → first 10,000 words of its Directions section) | ≥ 16 of 20 subsamples at p < 0.01 | **0 of 20.** Names 14–16% vs matched words 37–38%. FAIL |
| False positives (10 generator samples) | 0 of 10 at p < 0.01 | 0 of 10 (p 0.09–1.0). PASS |

## The Voynich numbers (unscored, because the test is VOID)
| Set | Eligible types | Found in the recipes | Frequency-matched expectation | Excess | p |
|---|---|---|---|---|---|
| Pharma labels (primary) | 90 of 189 | **71.1%** (64 types) | 68.2% (sd 3.4) | +2.9 points | 0.24 |
| Herbal-A first words (secondary) | 25 of 67 | 48.0% | 42.0% | +6.0 | 0.32 |

Most pharma labels are ordinary words that occur all over the book (okaiin, okain, otal, otar, chol, dar, shol…), so
they appear in the recipes, but no more than other pharma-page words of the same frequency. Pharma labels and their
matched words are also spread over the same number of pages (21 vs 20), so the Voynich null is not biased by
burstiness. **Taken at face value, there is no ingredient link; but the test has not shown it could see one.**

## Why the power control failed (post-hoc diagnosis, descriptive)
- Culpeper's plant names **do** recur in its Directions section as a whole: 98.7% of the 461 eligible names occur in
  the full 125,000-word section, against 88% for frequency-matched entry words and 93.5% for words matched on both
  frequency and dispersion. The link is real in a real compendium, and modest.
- The pre-registered target, the **first 10,000 words**, is the section's preamble on how to make syrups, conserves and
  oils in general. It names few plants (16%), and frequency-matched words, which are spread across the book, appear
  there at 41%. The target window, not the method, killed the control.
- A smaller second issue: content nouns are bursty (a plant's name sits in its own entry), so frequency matching alone
  favours the comparison words; dispersion matching narrows the gap (47% vs 16% in the preamble window) but does not
  remove the window problem.

## What this leaves
The question stands unanswered, and the Voynich side looks like "no link" at 10,000 tokens of recipes. A second
attempt would change only the power control (10,000-word windows drawn from across the whole Directions section) and
leave the Voynich statistic exactly as computed here. Its outcome is therefore already half known: if the new control
passes, the pre-registered NOT FOUND factor applies (L × 0.82, C × 0.9); if it fails too, the question is closed as
untestable at this size. This is recorded here before any new control is computed.
