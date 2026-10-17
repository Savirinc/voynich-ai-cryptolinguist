# E016 pre-registration: known-answer cracking test for the E014 cipher class

Written 2026-10-17, BEFORE the full run. Executed before writing: a 40k-letter Latin prototype (scratchpad; 2
restarts x 600k iterations: restart 1 reached 98.6% character accuracy, restart 0 failed) and a smoke run of this
script (20k iterations, 1 restart). Neither is used in the decision.

## Question
If Voynich were the E014 model (published Naibbe glyph inventory, unknown letter assignment, sandhi spelling choice,
~2% one-glyph nulls, ~1% ditto, ~4% merged words, line-final iin -> m), could our attack recover the plaintext from a
Voynich-sized text without being told the language? And can it tell success from meaningless input?

## Tasks (experiments/e016_verbose_known_answer.py, seed 16016)
- Secret key: published glyph strings, letters permuted independently within each (state, table).
- Plaintext: role=tune books (never in any LM), cleaned (Greshko clean_line), non-overlapping 40,000-letter
  stretches: la 3 keys, it 5 keys (all the tune text available).
- A: full size, attacked with each of the la, it, fr, de no-space LMs. B: 10,000 letters, true-language LM only.
- C (controls, full size, la LM): letter-shuffled la plaintext through the same cipher (3 keys); rugg_rep meaningless
  output with the same sandhi/null machinery (3 seeds).
- Attack: vcl.solvers.verbose.attack, 4 restarts x 600,000 SA iterations, best score kept.

## Decision rules (fixed now)
- CRACKABLE if character accuracy >= 0.80 with the true-language LM in >= 80% of the 8 A tasks.
- LANGUAGE IDENTIFIED if the lowest-gap LM is the true language in >= 80% of the A tasks.
- Confidence threshold for step 3 = the lowest gap reached by any control. Reported: how many successful A tasks
  fall below it (a usable threshold needs all of them below).
- Quarter size: reported, no decision.

## What follows
Only if CRACKABLE and a usable threshold exists does step 3 (attack Voynich DEV with the same procedure, compare its
gap to the threshold; locked leaves untouched) go ahead. If not, the failure mode tells us what to improve.
This test assumes the published inventory; a Voynich inventory that differs from Greshko's is not covered.
