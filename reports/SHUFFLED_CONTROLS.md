# E015: does the cipher twin need meaningful plaintext?

Pre-registration: reports/E015_PREREG.md (sha256 3f103b50…, locked 14:27Z). Results experiments/results/e015.json.

## Pre-registered verdict: MEANING DETECTABLE (real beats letter-shuffled in 3 of 4 languages)
| lang | real fit / held | letter-shuffled fit / held | word-shuffled fit / held | real vs letters |
|---|---|---|---|---|
| la | 1.10 / 0.99 | 1.64 / 1.07 | 1.04 / 0.88 | REAL (fit p 8e-8) |
| it | 1.31 / 1.08 | 1.76 / 1.21 | 0.94 / 0.94 | REAL (fit p 4e-7) |
| fr | 1.01 / 0.93 | 1.19 / 0.78 | 0.99 / 0.69 | REAL (fit p 2e-4; held favours shuffled at p 0.011, just above alpha) |
| de | 1.09 / 0.85 | 1.02 / 0.85 | 1.27 / 0.70 | not distinguishable |
Floors: FIT p90 1.40, HELD p90 1.11. Replicated on held-out ref text (same ordering).

## What it means, precisely
- The advantage is driven mainly by the hapax share: letter-shuffled input makes too many one-off words (z +2.5 to
  +4.3 vs +1.2 to +1.6 for real; fr real -0.7). Real plaintext has repeated letter sequences (real words), which the
  cipher turns into repeated Voynich words.
- **Word-shuffled input fits as well as or better than real text** (it, fr, de held). So the signal is
  WORD-LEVEL letter structure, not syntax or sentence meaning. A meaningless text built from real words (a word list,
  glossolalia over a real lexicon) would pass equally.
- Letter-shuffled input is still a full twin for fr and de, so the margin is modest.

## Status of the working model
Verbose homophonic cipher + context-dependent spelling + ~2% nulls, over plaintext with real word structure. This
favours "a real text underneath" over "random letters" under this model, but cannot distinguish a real text from
real words in random order, and does not identify the language.
