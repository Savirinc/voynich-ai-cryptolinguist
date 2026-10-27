# E087 pre-registration: the validated letter attack with spaces removed, one line = one record

Written 2026-10-27, before the run, at Arham's direction ("yes" to the spaceless attack). Follows E086 (spaces
mechanical; lines independent). Script `experiments/e087_spaceless_attack.py`; output `experiments/results/e087.json`,
`e087_run.log`; report `reports/SPACELESS_ATTACK.md`.

## What changes from E063/E080
- Voynich: each DEV prose line (Currier A 1,209 lines, B 2,102) is one sequence of S3 sign units (23 commonest kept),
  **spaces removed**.
- Plaintext: each language with spaces removed, cut into chunks with exactly the Voynich A lines' sign counts.
- Language model: 4-gram Kneser–Ney over continuous letters, chunks of 10 words joined without spaces, chunk breaks the
  only separator (first 60% of the text; plaintext from the rest).
- Score: **COVER** = share of decoded letters inside dictionary words (≥ 3 letters, frequency ≥ 2 in the model text) in
  the best segmentation of each decoded line (dynamic programming, words up to 12 letters). This replaces lexrate,
  because there are no given word breaks.
- Everything else as E063: VOY23 homophone encoder with 12% slips for the cracks, 32 restarts × 30,000, many-to-one.
- Controls: 2 copy-generator texts (seeds 31, 32, line by line), 5 pseudo-Voynich-A line texts (order-2 Markov over
  signs within lines), 5 pseudo-Voynich-B line texts.

## Languages (8)
Hebrew, Aramaic (Onkelos), Judeo-Arabic (Saadia), Talmud (Hebrew–Aramaic), Latin, Turkish, German, Arabic
(consonantal).

## Rules
VALIDATED iff both cracks reach accuracy ≥ 0.80 and agreement ≥ 0.95 and the lower crack COVER exceeds every A
control's; T = midpoint. CLAIM iff validated, agreement ≥ 0.95, COVER ≥ T and > the control maximum + 0.05.
| Outcome | Next | Ledger |
|---|---|---|
| CLAIM | blind reading, then a LOCKED_TEST prediction | none until confirmed |
| NO CLAIM, validated | the spaceless line form is excluded for these languages within this scope | recorded |
| not validated | that language untested spaceless | none |

## Disclosed
E086 results. Design counts above. No spaceless attack has been run. One attempt.
