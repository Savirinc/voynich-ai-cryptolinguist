# E013: edge-aware Voynich twins

Pre-registration: reports/E013_PREREG.md (sha256 799a516e…, locked 12:38Z before the full run).
Results: experiments/results/e013.json; log experiments/results/e013_run.log; code experiments/e013_edge_twins.py,
src/vcl/synthetic/edge_twins.py, tests/test_edge_twins.py.

## Pre-registered verdicts
- **TWIN (FIT, 13 features incl. edge coupling, y->q, line-final m): yes** for the published Naibbe cipher with
  context-dependent homophone choice, on all four plaintext languages (fit 0.94-1.02 vs Voynich floor p90 1.37;
  same on held-out ref text, 0.96-1.03). Without the mechanisms: 1.79-1.89 (E011c-like). Rugg 1.47, self-citation 2.86.
- **Necessary mechanism: sandhi only** (switching it off costs +0.54 to +0.70). Respacing (+0.28 only for de) and
  line-end m (+0.12 to +0.17) are not necessary by the 0.25 rule.
- **Identifiability: MEANINGFUL FAVOURED** (best Naibbe-edge/de held 1.70 vs best meaningless rugg_edge 3.37,
  Mann-Whitney p 7e-8). The meaningless generators fail type_hapax (z -8 to -9), qo_share and word-length features.

## Caveats that limit the claim
1. The coupling matrix C is fitted to Voynich, so matching edge_excess and y->q is partly by construction. What is
   NOT by construction: one weak mechanism (choose among ~4-6 equivalent spellings, beta ~1.5-2.8) is enough, and it
   keeps every other FIT feature in range.
2. **Held-out features are not matched.** Naibbe-edge held distance 1.55-1.88 vs Voynich's own held floor p90 1.12,
   and the mechanisms do not improve them vs all-off (1.63-1.84). Persistent misses: adj_repeat (z -2.7 to -3.1, Voynich
   repeats adjacent words more), wl_1 (z -1.7 to -2.9, too few 1-glyph words), type_hapax (z +2.3 to +3.3).
3. "Meaningful favoured" holds against these two meaningless designs only.
4. Plaintext language is not identifiable (la/it/fr/de within noise of each other).

## Reading
A verbose cipher whose writer picked among equivalent spellings according to how the previous word ended explains
the edge coupling with one parameter; random respacing and line-end abbreviation add little. The remaining gap
(adjacent repeats, one-glyph words, hapax) is the next target: a mechanism for word repetition (e.g. repeated
plaintext units, ditto marks, null/filler words) is the obvious candidate.
