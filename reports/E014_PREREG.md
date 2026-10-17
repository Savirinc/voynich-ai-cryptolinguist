# E014 pre-registration: repetition mechanisms on the edge-aware twins

Written 2026-10-17, BEFORE the full run (only a 3+3-evaluation Latin smoke run was executed to check the code; its
numbers are not used). Changes after the first full run are a new version, logged in experiments/FAILURES.md.

## Question
E013: Naibbe + context-dependent homophone choice reaches Voynich's FIT floor, but held-out adjacent repeats
(z ~ -2.7 to -3.1), one-glyph words (z ~ -1.7 to -2.9) and hapax share (z ~ +2.3 to +3.3) are missed. Do three
repetition mechanisms close that gap without breaking the remaining independent features, and which are needed?

## Mechanisms (src/vcl/synthetic/rep_twins.py), on top of the E013 mechanisms
1. **nulls** p_null in [0, 0.08]: one-glyph filler words from the Voynich DEV one-glyph words that are not Naibbe
   unigram glyphs (s, l, r, o, d, ...; 'y' excluded); decodable by dropping them.
2. **ditto** p_rep in [0, 0.03]: a word written twice.
3. **memory** (Naibbe only) p_reuse in [0, 0.9], mem_window in [1, 60]: reuse the previous spelling of a recently
   enciphered unit (decodable).
Meaningless families (rugg_rep, self_citation_rep) get nulls and ditto (memory has no analogue).

## Features
FIT (16) = E013 FIT + adj_repeat + wl_1 + type_hapax. HELD (6, never searched): double_rate, word_top_share,
h3_cond, zipf_slope, ed1_types, qo_share. Everything else as E013 (seed 14014; 140 + 160 evaluations per combo,
decoys 3x; 20 final samples; ref text for held-out plaintext).

## Decision rules (fixed now)
- **TWIN**: final mean FIT distance <= Voynich FIT floor p90.
- **FULL TWIN**: TWIN and final mean HELD distance <= Voynich HELD floor p90 (both floors computed on these lists).
- **NECESSARY mechanism**: switching it off raises mean FIT distance by > 0.25 (ablations: nulls, ditto, memory,
  sandhi).
- **Identifiability**: held-out distances of best meaningful vs best meaningless, two-sided Mann-Whitney, p < 0.01.

## Limits
The new FIT features are no longer independent checks; only the six HELD features are. Fitting more knobs to more
targets can always improve FIT, so the informative outcomes are HELD, the ablations, ref-text replication and the
meaningful-vs-meaningless comparison. No decipherment is attempted.
