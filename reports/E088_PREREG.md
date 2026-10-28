# E088 pre-registration: spaceless line-by-line attack for the Hebrew family, with a yardstick chosen on known answers

Written 2026-10-28, before the run, at Arham's direction ("yes let's do that"), to repair E087's gap: E087's decoder
cracked every Hebrew-family known answer, but its coverage yardstick ranked junk above correct decodes in consonantal
scripts, so Hebrew, Aramaic, Judeo-Arabic, Talmud and Arabic were untested. Script
`experiments/e088_spaceless_hebrew_family.py` (decoding functions imported unchanged from the locked E087 v3); output
`experiments/results/e088.json`, all decoded lines in `experiments/results/e088_decoded.json`, log `e088_run.log`;
report `reports/SPACELESS_HEBREW.md`.

## Decoding
Exactly E087 (spaces removed, one Voynich DEV prose line per sequence, 23 S3 signs; plaintext without spaces cut to the
Voynich A line lengths; 4-gram KN letter model; 32 restarts × 30,000; 2 cracks, 2 generator + 5 pseudo-A controls,
Voynich A, 5 pseudo-B controls, Voynich B), seed 88088, languages: Hebrew, Aramaic (Onkelos), Judeo-Arabic (Saadia),
Talmud, Arabic. Every decoded line is saved, so later yardsticks need no rerun.

## Yardstick chosen on known answers only (before any Voynich score is read)
Candidates: COVER4 and COVER5 (share of decoded letters inside dictionary words of ≥ 4 or ≥ 5 letters, best
segmentation); PAIR (best unigram segmentation, then mean word-pair association log P(b|a) − log P(b) over adjacent
known words). A yardstick validates a language if both cracks are cracked (accuracy ≥ 0.80, agreement ≥ 0.95) and the
lower crack score exceeds every A control. Chosen: the yardstick validating most languages; ties by the larger mean
normalised gap (min crack − max control) / (max crack − min control). The script makes this choice automatically.

## Claim rule (chosen yardstick)
CLAIM iff validated, agreement ≥ 0.95 and score ≥ T = (min crack + max A control) / 2; for B also > max B control.
| Outcome | Next |
|---|---|
| CLAIM | blind reading by Hebrew/Arabic readers, then a LOCKED_TEST prediction |
| NO CLAIM, validated | the spaceless line form excluded for that language within scope |
| not validated | untested |

## Disclosed
E086, E087 (all numbers). Smoke test on Hebrew only at 2 restarts × 200 iterations (not the registered effort): crack
accuracy 0.79–0.80 (below the bar), COVER5 separated cracks from controls (normalised gap +0.25) while COVER4 (−0.35)
and PAIR (−1.0) did not at that effort; Voynich A COVER5 0.055 vs control 0.088 at that effort. These smoke files were
deleted; no full-effort result exists. One attempt.
