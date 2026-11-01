# E118 pre-registration (Arham, move 4, 2026-11-01): can any attack of a given cipher class work at Voynich length?

Script `experiments/e118_unicity_budget.py` (sha256 in the commit). **The Voynich is not decoded.** Only its sign
inventory and sign frequencies are used, as in E047. Everything is a known answer.

## Question (Shannon's unicity distance, measured)
A cipher class can be attacked only if the text is long enough that wrong keys stop fitting as well as the right key.
X096 found free keys fitting the book as well as crib keys. Before more attacks: for each class we rely on, is
28,841 words (Voynich A 8,806) enough?

## Classes (declared now; no others, rule 9)
- **K1, letter cipher (VOY23, the E047/E049/E063 class):**
  - many-to-one homophones over the 23 commonest Voynich-A signs;
  - 12% spelling slips;
  - E047's attack, unchanged.
- **K3, whole-word code:** one plaintext word ↔ one code word, one-to-one. This is the easiest kind of code for an
  attacker; nomenclators with homophones are harder. Never attacked by decipherment in this project; E098 judged the
  nomenclator only on the 13-feature battery.

## Part A: K1 length ladder
- **Lengths:** 125, 250, 500, 1,000, 2,000, 4,400, 8,806 words.
- **Ciphers:** 4 fresh keys × 3 languages (Hebrew, Turkish, Latin), plaintext from the TEST books, LM from the disjoint
  LM books.
- **Scores:**
  - CRACK = letter accuracy ≥ 0.80.
  - SPURIOUS restart = it scores at least as well as the *true* key, yet has accuracy < 0.80.
- **U1** = the shortest length with ≥ 9 of 12 cracks.
- **Unscored:** one copy-generator stream per length (agreement only).

## Part B: K3 at full Voynich length
- **Plaintext:** 28,841 consecutive TEST-book tokens per language.
- **Model:** word-bigram model from the disjoint LM books, absolute discounting 0.75, top 4,000 words. Every keyed
  plaintext word the model lacks is appended with zero count. That favours the attacker, because the true key can
  always be written down.
- **Attack:**
  - the 1,000 commonest code words;
  - the rest left unknown in every key;
  - start from frequency-rank matching;
  - rank-local proposals;
  - 4 restarts × 20M annealing steps.
- **Equivocation:**
  - SPURIOUS = the best key found scores at least as well as the true key;
  - ORACLE DRIFT = a gentle search (5M steps) started *at* the true key ends scoring at least as well, with accuracy
    more than 0.10 lower.
- **Unscored bound:** the same with an in-sample model (the plaintext itself, perfect knowledge). Its rank start is
  already the true key, so only its oracle probe is informative.

## Decision table (no ledger factor: this is a budget, except where marked *)
| Class | Outcome | Rule | Consequence |
|---|---|---|---|
| K1 | DECIDABLE WITH MARGIN | U1 ≤ 4,400 | letter-attack absence results stand |
| K1 | DECIDABLE, TIGHT | U1 = 8,806 | stand; attacks on parts shorter than Voynich A (single sections) are not informative |
| K1 | UNDECIDABLE* | no length reaches 9/12 | letter-attack absence factors withdrawn by a locked amendment |
| K3 | DECIDABLE | accuracy ≥ 0.50 in ≥ 2 of 3 languages | a word-code attack is worth building |
| K3 | UNDECIDABLE | accuracy < 0.50 in all 3 and (SPURIOUS or ORACLE DRIFT) in ≥ 2 of 3 | retired from statistical attack; only cribs or outside evidence can test it; no past absence result applied to it |
| K3 | SEARCH-LIMITED | otherwise | inconclusive |

Rule 8 does not apply: there is no Voynich value near a boundary.

## Seen beforehand (development, DEV books, dev seeds, no Voynich)
- **Already known:** E090 cracked 30/30 K1 ciphers at Voynich-A length.
- **K3 development:** step count and temperature were tuned on DEV books. A bug was found and fixed: one unknown slot
  shared by many code words let the search inflate its score.
- **With the fix, at 20M steps × 2 restarts:**
  - accuracy 0.26 (Hebrew), 0.32 (Turkish), 0.33 (Latin); frequency-rank baseline 0.03 / 0.07 / 0.13;
  - every best key scored *above* the true key;
  - the oracle drifted in all three (0.65 → 0.34, 0.65 → 0.36, 0.77 → 0.52);
  - with the in-sample model the oracle stayed put (0.64 / 0.64 / 0.77).
- The TEST-book run may differ. The decision table is fixed regardless.
