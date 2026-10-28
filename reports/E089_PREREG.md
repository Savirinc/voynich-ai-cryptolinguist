# E089 pre-registration: spaceless line-by-line attack with mixed-language models

Written 2026-10-28, before the run, at Arham's direction ("have we tried Voynich without considering spaces, with a
language that may take parts from multiple languages?" → "yes"). Script `experiments/e089_spaceless_mixtures.py`
(E088 decoding, yardstick candidates and selection rule imported unchanged; E084 mixture streams); output
`experiments/results/e089.json`, decoded lines `e089_decoded.json`, log `e089_run.log`; report
`reports/SPACELESS_MIXTURES.md`.

## Mixtures (10-word stretches alternating, as E084)
Hebrew-containing: Hebrew + Aramaic (Onkelos); Hebrew + Judeo-Arabic (Saadia); Hebrew + Aramaic + Judeo-Arabic (three
way); Hebrew transliterated (E062 table) + Latin; Hebrew transliterated + Turkish. Comparisons: Latin + German; Latin +
Turkish. Greek mixtures left out (a second alphabet would not fit the 23-letter decoder).

## Procedure and rules
Exactly E088: spaces removed, one Voynich DEV prose line per sequence; model from the first 60% of each stream,
plaintext from the rest cut to Voynich A line lengths; 2 cracks, 2 generator + 5 pseudo-A controls, Voynich A, 5
pseudo-B controls, Voynich B; 32 × 30,000; seed 89089. Yardstick (COVER4, COVER5, PAIR) chosen automatically on known
answers only; CLAIM rule as E088.
| Outcome | Next |
|---|---|
| CLAIM (any mixture) | blind reading, then a LOCKED_TEST prediction |
| NO CLAIM, validated | the spaceless line form excluded for that mixture within scope |
| not validated | untested |

## Disclosed
E084 (mixtures with spaces: no claim), E087, E088. Smoke test (Hebrew + Aramaic only, 2 restarts × 200 iterations, not
the registered effort) ran end to end; its numbers are meaningless at that effort and its files were deleted. Stream
sizes: 163,140–1,224,440 words. One attempt.
