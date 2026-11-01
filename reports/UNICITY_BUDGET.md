# E118: can any attack of a given cipher class work at Voynich length? (Arham, move 4)

Pre-registration `E118_PREREG.md` (sha256 5a8fa043…), script `experiments/e118_unicity_budget.py` (sha256 c56cacad…),
results `experiments/results/e118.json`, log `e118_run.log`. Run 2026-11-01, 2,341 s. Known answers only; the Voynich
was not decoded.

## Part A: K1 letter cipher (VOY23, the class of E047/E049/E063)
| Length (words) | 125 | 250 | 500 | 1,000 | 2,000 | 4,400 | 8,806 |
|---|---|---|---|---|---|---|---|
| Keys recovered (of 12) | 12 | 12 | 12 | 12 | 12 | 12 | 12 |
| Texts with a wrong key fitting as well as the true one | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**U1 = 125 words: DECIDABLE WITH MARGIN.** Voynich A is about 70 times longer than the decoder needs, so the
letter-attack absence results stand.

**Unscored lesson:** on copy-generator streams the restarts also agree perfectly (agreement 1.00 at every length).
"The restarts agree" therefore does not mean "a key exists". Only the lexical gate separates real text from gibberish.
Reports that read low agreement as a sign of "no key" (e.g. `VOYNICH_ATTACK.md`, agreement 0.50–0.74) over-read it.

## Part B: K3 whole-word code (one word ↔ one code word), 28,841 tokens
| Language | Accuracy (best of 4) | Rank-match baseline | Ceiling (top 1,000 code words) | Best key vs true key score | Oracle: start at true key → ends at |
|---|---|---|---|---|---|
| Hebrew | 0.04 | 0.02 | 0.57 | −123,944 vs −156,173 (**wrong key fits better**) | accuracy 0.11, score above true |
| Turkish | 0.20 | 0.04 | 0.63 | −126,360 vs −148,713 (**better**) | 0.31, above true |
| Latin | 0.24 | 0.14 | 0.75 | −131,504 vs −156,721 (**better**) | 0.40, above true |

With a perfect-knowledge model (the plaintext itself, unscored bound) the true key holds, and the oracle stays at
0.56 / 0.63 / 0.75.

**Verdict: UNDECIDABLE.** With any realistic model (one built from other texts of the same language and genre), many
wrong keys fit a Voynich-length word code *better* than the true key. A search started *on* the true answer walks away
from it. The information to pick out the right key is not in 28,841 words; it would have to come from outside the text.

## What this means
- **Letter ciphers:** fully attackable at Voynich length. Our "no letter cipher found" results are informative.
- **Whole-word codes (nomenclator-type):** not attackable by statistics at this length, however clever the search.
  This class is **retired from statistical attack**. Only cribs (a known word at a known place, e.g. labels next to
  pictures; move 5) or outside evidence could test it. No past absence result in the ledger applied to it.
  - E098's nomenclator CLASS FAILS still stands: it was judged on the text's statistical shape, not by decipherment.
- **Caveat:**
  - part of the true key's poor score comes from words the model never saw (appended at zero count), which is exactly
    what a real attacker faces;
  - only the most attacker-friendly code was tried; homophonic codes are harder still.

No ledger factor (pre-registered as a budget); ledger unchanged (M 0.8860, L 0.0803, C 0.0151, O 0.0186).
