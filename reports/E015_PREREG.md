# E015 pre-registration: does the E014 twin need MEANINGFUL plaintext?

Written 2026-10-17, BEFORE the full run (only a 3+3-evaluation Latin smoke run was executed; numbers unused).

## Question
E013/E014 favoured "meaningful" over two meaningless generators, but those decoys used different machinery. The
fair decoy is the SAME cipher model (E014 naibbe_rep: published Naibbe tables + sandhi + nulls + ditto + memory +
respacing + line-end m) fed meaningless input with identical letter statistics.

## Conditions (per language la, it, fr, de; same E011 tune/ref chunks)
- real: chunks unchanged.
- shufword: word order shuffled within each chunk (real words, no syntax).
- shufchar: all letters shuffled within each chunk, spaces kept in place (same letter frequencies; no words).
Shuffles are deterministic (crc32 of book id, offset, condition).

## Procedure
Identical to E014 (features FIT 16 / HELD 6, standardisation, floors, search 140 + 160, seed 15015, 20 final samples
on tune and ref text), each condition searched independently with the same budget.

## Decision rules (fixed now)
Per language, real vs shufchar, two-sided Mann-Whitney on the 20 final-sample distances, separately for FIT and
HELD, alpha 0.01:
- REAL FAVOURED: real significantly lower on FIT or HELD and shufchar not significantly lower on either.
- SHUFFLED FAVOURED: the reverse. MIXED: both. Otherwise NOT DISTINGUISHABLE.
- Overall: "MEANING DETECTABLE" if REAL FAVOURED in >= 3 of 4 languages; otherwise "MEANING NOT DETECTABLE by these
  statistics under this cipher model". shufword is reported descriptively (no decision).

## Interpretation fixed in advance
If letter-shuffled input fits as well as real text, the E013/E014 "meaningful favoured" results only showed that the
cipher MACHINERY fits better than the decoy machinery, not that Voynich encodes language. If real wins, the
statistics carry a signature of real plaintext structure (letter order), which supports a meaningful text under this
model (still no decipherment).
