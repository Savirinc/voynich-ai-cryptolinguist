# E014: repetition mechanisms on the edge-aware twins

Pre-registration: reports/E014_PREREG.md (sha256 5ccf565f…, locked 13:24Z before the full run).
Results: experiments/results/e014.json, e014_run.log; code experiments/e014_rep_twins.py, src/vcl/synthetic/rep_twins.py,
tests/test_rep_twins.py.

## Pre-registered verdicts
- **FULL TWIN (FIT 16 features <= floor p90 1.40 AND HELD 6 features <= floor p90 1.11): yes, for Naibbe on all four
  languages** -- la 1.13/0.92, it 0.93/0.96, fr 1.07/0.68, de 0.93/0.77; replicated on held-out ref plaintext
  (fit 0.89-1.12, held 0.79-1.02). Rugg 1.45/2.20 and self-citation 3.71/9.43 are not twins.
- **Necessary mechanisms**: sandhi (+0.49 to +0.54, every language); nulls only for la (+0.32) and de (+0.37);
  ditto and spelling memory are never necessary.
- **Identifiability: MEANINGFUL FAVOURED** (de held 0.77 vs rugg 2.20, Mann-Whitney p 7e-8).

## Fitted values (small and plausible)
sandhi: choice among 3-7 equivalent spellings, beta 1.7-2.4; one-glyph nulls 1.0-3.1% of words; ditto 0.2-1.5%.

## What this does and does not add
- The six HELD features were ALREADY within the floor for the E013 model (RMS z 0.66-0.93 on the same six), so the
  FULL TWIN status is not new independent evidence. E014 shows the three E013 misses (adjacent repeats, one-glyph
  words, hapax share) are reachable with small, decodable additions without breaking anything else.
- type_hapax stays at the edge (z +1.8 to +2.0 for la, fr, de; +1.0 for it).
- Plaintext language remains unidentifiable (la/it/fr/de all fit).
- "Meaningful favoured" is relative to two meaningless designs; self_citation's qo_share failure (z -21) suggests
  that implementation is a weak decoy, so this comparison should be repeated with a stronger meaningless generator
  given the same sandhi/null machinery.

## Working model of how the text was made
A verbose homophonic cipher (Naibbe-like: each word = 1-2 plaintext letters) whose writer chose among equivalent
spellings according to how the previous word ended, plus ~2% one-glyph filler words. It reproduces every Voynich
statistic we measure, within Voynich's own page-to-page variation. It does NOT identify the tables, the language or
any word meaning.
