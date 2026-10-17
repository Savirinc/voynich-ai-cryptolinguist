# E013 pre-registration: edge-aware Voynich twins

Written 2026-10-17, BEFORE the full run. Only a smoke run (3+3 search evaluations, 2 final samples, Latin only)
was executed, to check that the code runs; its numbers are not used. Any change after the first full run is a new
version, logged in experiments/FAILURES.md.

## Question
E011/E011c: the faithful Naibbe cipher (Greshko 2025) matches Voynich's main statistics but not the word-edge
coupling (E012: shuffle-corrected last-glyph -> first-glyph MI 0.19 bits; Naibbe 0.002-0.005), y->q adjacency,
line-final m, adjacent repeats or the hapax share. Can three candidate mechanisms close that gap, which of them are
needed, and does the best fit require a meaningful cipher?

## Mechanisms (src/vcl/synthetic/edge_twins.py)
1. **sandhi**: each word is chosen among k equivalent candidates with weight exp(beta * C[prev last glyph, first
   glyph]). Naibbe candidates encode the same plaintext unit (text stays decodable; tested).
2. **respacing**: split (p_split, at a position favoured by C, strength beta_s) and merge (p_merge, preferring
   weak joins).
3. **line_end**: line-final ...iin / ...in -> ...m with probability p_m.

C is estimated from Voynich DEV prose lines (common glyphs only, shrunk, clipped to +-3). It is target-derived.

## Families
- naibbe_edge: published Naibbe tables, plaintext la, it, fr, de (E011 tune books; ref books for held-out text).
- rugg_edge (Rugg 2004 grille) and self_citation_edge (Timm & Schinner): same three mechanisms; 3x search budget.

## Fingerprint and features
E011 machinery (DEV prose blocks of ~12,000 symbols, LOCKED_TEST never read; standardisation by Voynich block SD;
RMS z distance; noise floor = leave-one-out distance of Voynich blocks).
- FIT (search target, 13): E011 FIT + edge_excess (shuffle-corrected, 5 within-line shuffles) + yq_logor +
  mfinal_logor.
- HELD (never used by the search, 9): double_rate, word_top_share, wl_1, h3_cond, type_hapax, zipf_slope,
  adj_repeat, ed1_types, qo_share.

## Search and evaluation
Random search 140 + local refinement 160 per combo (decoys 3x), seed 13013. Final evaluation: 20 fresh samples per
best spec on tune text (and 20 on ref text for Naibbe), plus the same spec with each mechanism switched off (three
ablations) and with all three off.

## Decision rules (fixed now)
- **TWIN**: a combo whose final-eval mean FIT distance is <= the Voynich FIT noise floor p90.
- **NECESSARY mechanism**: switching it off raises the best combo's mean FIT distance by > 0.25.
- **Identifiability**: held-out distances (20 samples each) of the best meaningful vs the best meaningless combo,
  two-sided Mann-Whitney; p < 0.01 -> the lower one is favoured; otherwise NOT IDENTIFIABLE.
- Reported regardless: per-feature z for each combo; whether the held-out features that E011c missed
  (adj_repeat, type_hapax, wl_1) improve vs the all-off version.

## What this cannot show
A twin shows a mechanism class can produce Voynich-like text; it does not decipher anything. Because C is fitted to
Voynich, matching edge_excess and yq_logor is partly by construction. The informative outcomes are the held-out
features, the ablations and the meaningful-vs-meaningless comparison.
