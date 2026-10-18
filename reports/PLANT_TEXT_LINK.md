# E022 (methodology A2b): do plants that look alike have pages with alike words? — NOT DETECTED

Pre-registered: reports/E022_PREREG.md (sha256 26359c5b…). Visual codes: data/derived/e022_visual_codes_A.json
(blind coder agent, images only; locked read-only before analysis, sha256 b5a9698d…). Script:
experiments/e022_plant_text_link.py. Results: experiments/results/e022.json.

## Result
| | Value |
|---|---|
| Pages | 100 (101 coded; one has no clean prose tokens) |
| Pairs ≥ 4 folios apart | 4,441 |
| Spearman r (visual vs text similarity) | **0.015** |
| Permutation p (within Currier language × hand) | **0.55** |
| Verdict | **NOT DETECTED** |
| All pairs: r, p | 0.016, 0.56 |
| Currier A hand 1 only: r | 0.007 (2,256 pairs) |
| First word shared, top-10% most similar pairs vs rest | 0/523 vs 0.05% |

## Reading (as pre-registered)
No sign that page text tracks what the drawn plant looks like. That doesn't prove the text is meaningless.

## Limits, including one that should have been in the pre-registration
- **No power check.** The test was not first run on a real illustrated herbal, so we don't know how large r would
  be if the text were meaningful. Medieval herbal text mostly gives names, virtues and preparations, not
  appearance, so plain language could also give r ≈ 0. Without a positive control a null is weak evidence.
  Future meaning tests must include one (rule added to METHODOLOGY.md).
- Coarse, single-coder visual coding: most plants share the common values (branched root, several flowers,
  green leaves).
- Voynich herbal pages almost never share their first word: 1 shared first word in ~5,000 pairs.

## Update after E023 (power check)
The same test on a real herbal (Culpeper) also finds nothing (r −0.012, p 0.68). The test has no power for herbal
text, so the Voynich null is uninformative. Line dropped (see HERBAL_POWER_CHECK.md).
