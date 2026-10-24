# E053 pre-registration: abbreviated Latin (the L-abbrev form), technical and sacred

Written 2026-10-24, before the run. Script: `experiments/e053_abbrev_latin.py`. LOCKED_TEST is not used. Updates
`reports/LEDGER.md` through the absence rule.

## Question
Learned 15th-century writing was full of standard abbreviations. Could Voynich be **abbreviated Latin** written letter
by letter in an invented 23-sign script? Abbreviation shortens words, bringing them closer to Voynich's 3.6 signs, and
it would explain the plain Latin search (E049) failing.

## Data
Gaskell & Bowern's abbreviated Latin texts (their meaningful set, commit d076a7d0; used locally, not
redistributed):
- **abbr_tech:** Pliny's *Natural History*, abbreviated (407,547 tokens);
- **abbr_sacred:** the Vulgate New Testament, abbreviated.

For each text:
- **Preparation:** lowercase, whitespace tokens, the 23 commonest characters kept (abbreviation signs such as '9'
  included if they are common).
- **Split:** the first 70% builds the LM; the last 30% supplies the known-answer plaintext.

## Method (identical to E052)
- **Per LM:** 2 VOY23 ciphers (fresh keys, 12% spelling slips) for validation; 7 controls (2 generator, 5
  pseudo-Voynich-A); and Voynich A.
- **VALIDATED / CLAIM:** exactly E052's rules (cracks ≥ 0.80 accuracy, agreement ≥ 0.95, cracks above every control;
  Voynich must reach the threshold and beat the best control by 0.05).
- A CLAIM leads to a blind reading and LOCKED_TEST confirmation.

## Absence rule (shares set now)
- **L-abbrev** is 0.15 of L.
- **This search covers "Latin abbreviated in a standard medieval style, written letter by letter"** at a share of
  **0.40 of L-abbrev**. Other languages' abbreviations, and other schemes, make up the rest.
- **The miss rate is m = 0.3,** higher than the default 0.2. One modern reconstruction of abbreviation stands in for
  many medieval schemes, so a mismatch is more likely.
- **If both LMs are validated with no claim:** L × (1 − 0.15 × 0.40 × 0.7) = **L × 0.958**.
- **If only one is validated:** half of that share is used.

## What was seen before writing this (disclosed)
- The first lines of the abbreviated Pliny, and its character frequencies.
- No attack with these LMs has been run.
