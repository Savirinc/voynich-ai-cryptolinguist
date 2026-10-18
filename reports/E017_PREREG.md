# E017 pre-registration: known-answer test, second attempt (portfolio attack + two-part confidence test)

Written 2026-10-18, BEFORE the full run. E016 (NOT CRACKABLE, no usable threshold) showed that success is a rare
search event and the LM gap is not a safe success signal.

## Development done before writing (scratchpad, NOT used in any decision)
All on DEVELOPMENT keys/seeds (50000+, 1001), never used by E016 or this test; plaintext = the same tune stretches.
- Delta scoring (src/vcl/solvers/fast_anneal.py; tested identical to the full score): ~10x faster per proposal.
- Restart length: 100k-iteration restarts succeeded more often on Latin (6/32) than 200k (3/32 + 2/9) or 2M (0/9);
  so the budget goes into many short restarts. A cipher-alphabet LM did not help (Latin 0/16 vs 2/16); not used.
- Successful restarts reproduce the same plaintext (agreement 0.965-0.994 between independent restarts). Controls
  and wrong-LM decodes reached up to 0.932 (rugg + German LM): agreement alone has too thin a margin.
- Coverage of decoded letters by 7-14-letter dictionary words (lexcov7): real cracks 0.144-0.153; controls and
  wrong-LM decodes 0.005-0.037. Neither signal alone is relied on; both are required.

## Tasks (experiments/e017_portfolio_known_answer.py, seed 17017; fresh keys and cipher seeds)
- A: full size (40,000 letters), la 3 keys + it 5 keys (same tune stretches as E016), each attacked with the
  la, it, fr, de no-space LMs (32 attacks).
- B: quarter size (10,000 letters), true-language LM only (8).
- C: controls, full size, each attacked with all 4 LMs: letter-shuffled la (3) and it (2) plaintext through the same
  cipher, rugg_rep meaningless output (3 seeds) (32).
- Attack: vcl.solvers.verbose.attack_portfolio, 128 restarts x 100,000 SA iterations, best objective kept.

## Decision rules (fixed now)
- CLAIM (per attack) iff agreement >= 0.95 AND lexcov7 >= 0.08 (vocabulary = top-60k words of the LM's ref books,
  cleaned with Greshko clean_line; decode cleaned the same way).
- Language pick per text = the claimed LM with the highest lexcov7 (none if no claim).
- CRACKABLE: true-LM character accuracy >= 0.80 in >= 80% of the 8 A texts.
- SAFE: zero CLAIMs among the 32 control attacks AND zero CLAIMs among A attacks with accuracy < 0.5.
- LANGUAGE IDENTIFIED: picked LM = true language in >= 80% of the 8 A texts (no pick counts as wrong).
- Step 3 GO (attack Voynich DEV with exactly this procedure and rule; LOCKED_TEST leaves untouched) only if
  CRACKABLE and SAFE and LANGUAGE IDENTIFIED. Reported regardless: margins (control maxima vs success minima),
  quarter-size results (no decision).

## What this cannot show
Plaintext stretches are the same as E016's and as the development runs (only the keys differ); the tune text
available allows nothing else. The cipher model assumes Greshko's published inventory and these four languages;
a Voynich NO CLAIM in step 3 would not exclude other inventories or languages. Plaintext that is heavily
abbreviated would lower lexcov7.
