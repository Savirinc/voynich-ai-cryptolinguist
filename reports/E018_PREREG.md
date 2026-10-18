# E018 pre-registration: step 3 — the E017 procedure applied to Voynich

Written 2026-10-18, BEFORE the full run (only a 4-restart x 20k smoke on Currier A with the Latin LM was run, to
check the code; not used). E017 passed all three gates (CRACKABLE 8/8, SAFE 0/32, IDENTIFIED 8/8), so step 3 is GO.

## Text
Voynich DEV prose words (28,841 tokens) in reading order (folio, line); unclear tokens dropped; LOCKED_TEST leaves
(15, incl. 1, 8, 9, 30, 35, 38, 51, 56) excluded and asserted excluded. Words that do not parse into the published
Naibbe inventory (~20%) are dropped, exactly as in E016/E017 (where ~5% were dropped).

## Procedure (frozen, unchanged from E017)
attack_portfolio, 128 restarts x 100,000 iterations, la/it/fr/de no-space LMs. CLAIM iff agreement >= 0.95 AND
lexcov7 >= 0.08. Seed 18018.

## Decision (fixed now)
- Primary: whole DEV text. CLAIM if any LM claims; language = the claimed LM with the highest lexcov7.
  -> If CLAIM: the decode is reported in full, then (separately pre-registered) decoded once on LOCKED_TEST with the
     same key as the confirmation test, plus the plant-pair and zodiac-label checks.
  -> If NO CLAIM: "Voynich is not the E014 cipher class with the published Naibbe inventory and la/it/fr/de
     plaintext, as far as this attack (validated in E017) can detect."
- Secondary (reported, no decision): Currier A and Currier B separately (in case they use different keys/languages).

## What this cannot show
A NO CLAIM does not exclude a different glyph inventory, other languages, heavily abbreviated plaintext, or other
cipher mechanisms. The 20% unparsed rate (vs ~5% in E017's synthetic texts) is itself evidence the inventory differs
from the author's.
