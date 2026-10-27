# E083 pre-registration: proof by construction - derive Voynich from Hebrew, then test the derivation

Written 2026-10-27, before the run, at Arham's direction: treat "Voynich is Hebrew-inspired" as a statement to be
proved, like LHS = RHS; stress-test Hebrew and its associates in non-standard forms; follow the prescription exactly.
Script `experiments/e083_hebrew_construction.py`; output `experiments/results/e083.json`, `e083_run.log`; report
section in `reports/HEBREW_CAMPAIGN.md`.

## The construction
A source word is cut into prefix + root + suffix (Hebrew, Aramaic, Judeo-Arabic: the Hebrew prefix and suffix lists of
E081; other sources: their 13 commonest beginnings and 17 commonest endings of 1–2 letters). It is rewritten as:
- front = table PT[prefix] (14 Voynich fronts, including none, *ok, ot, qok, qot*);
- bridge = the root's first M letters, each through table RT (30 Voynich chunks, or dropped); M ∈ {1, 2, 3, 4, all}
  (abbreviation allowed);
- ending = table ST[suffix] (23 Voynich endings, including none).
Fit: annealing over PT, RT, ST, M (60,000 steps, 3 restarts, best kept) to maximise the share of running text that
matches word for word in frequency between the transformed source (28,841 tokens from token 10,000) and Voynich DEV
prose (histogram intersection, 0–1).

## The three checks a proof must pass
1. **Known answer (validity).** A second Hebrew window (tokens 60,000–88,840) transformed by a hidden random table
   (M = 3) is the target; fitting from window 1 must decode ≥ 50% of its tokens to the exact source word, and its
   order test must give z > 3. Otherwise VOID.
2. **Specificity.** Best intersection over the Hebrew family (Hebrew with linguistic affixes, Hebrew with data-driven
   affixes, Aramaic Onkelos, Judeo-Arabic Saadia) must exceed the best over the others (Latin, Greek, German, Arabic,
   Turkish, letter-scrambled Hebrew) by > 0.05.
3. **Order.** Decode each Voynich token to the commonest source word that transforms to it; score consecutive decoded
   pairs with a word-bigram model (add-0.1) from the same source outside the fitted window; compare with 200 shuffles
   of Voynich's word order (line lengths kept). For the best Hebrew-family source: z > 3.

| Outcome | Rule | Next |
|---|---|---|
| **CONSTRUCTION HOLDS** | valid; checks 2 and 3 pass | blind reading by Hebrew readers; pre-registered LOCKED_TEST prediction; ledger only after those |
| HEBREW FITS BEST BUT ORDER FAILS | check 2 only | recorded; no factor |
| ORDER PASSES BUT FIT NOT HEBREW-SPECIFIC | check 3 only | recorded; no factor |
| CONSTRUCTION FAILS | neither | recorded; no factor |
| VOID | check 1 fails | none |

## Disclosed (seen beforehand)
E080–E082 (no claim for H1, H2, H3, H5). Before locking, the fitting code was exercised on the known-answer target only
(never on Voynich): 3,000 steps gave intersection 0.16 (2 s); 60,000 steps gave intersection 0.542 with 66.2% of tokens
decoded to the exact source word and M = 3 recovered (47 s); 200,000 steps gave 0.544 / 66.8%, so 60,000 was kept.
No source has been fitted to Voynich. One attempt.
