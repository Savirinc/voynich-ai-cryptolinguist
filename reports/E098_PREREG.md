# E098 pre-registration (Arham, 2026-10-30): can any of five untested period cipher classes make the Voynich's fingerprint?

Script `experiments/e098_cipher_classes.py` (sha256 in the commit). Locked before the Voynich is scored.

## Question
C (a cipher or code over a real language) stands at 0.0998. Its earlier movements were small (E049–E050 × 0.95, E062
× 1/3, E063 × 0.98); most of C is untested. For five cipher classes used or available around 1400–1450 that no earlier
test covered, can any setting produce the Voynich's measured profile?

## Classes, shares of C (judgement, fixed now) and settings (declared now; no others)
| Class | Share of C | Base | Settings |
|---|---|---|---|
| K1 nomenclator (code words for the N commonest plaintext words, letter cipher for the rest) | 0.20 | S | N 30, 50, 80, 120, 180, 260, 380, 550, 800 |
| K2 letters rearranged inside each word | 0.08 | S | reverse; sort by the units' mean position in the target's words; fixed permutation per word length |
| K3 null words mixed in (drawn from the target's 20 commonest words) | 0.12 | S, V | rate r 0.10, 0.15, …, 0.50 |
| K4 rotating tables (new table every k lines or every page) | 0.10 | S, V | k 1, 2, 3, 4, 6, 8, 12 lines; page |
| K5 abbreviation then cipher | 0.10 | S | vowels dropped after the first sound; first 3 sounds; first 2 + last 2 |
| Rest of C (classes tested before, other languages, other designs) | 0.40 | — | not tested here |

- **Base S:** many-to-one substitution of period sounds into the 23 VOY23 units, frequency-rank matched to the target
  (ranks jittered in blocks of 3 by seed).
- **Base V:** the Naibbe verbose cipher with permuted tables (as E062).
- **Generous to C:** code words and null words are the target's own commonest words, and unit ranks are matched to the
  target. A designer could have chosen exactly these.
- **K4 S tables:** the rank-matched table shifted cyclically by a block offset (Alberti-style).

**Plaintexts:** Latin, Italian, German, Occitan, Hebrew as period sound words (E097 corpora and rules), read cyclically
from a seeded offset.

**Sets and pouring:** set = class × setting × base × language (245 sets), 10 seeds each. Output is poured into the
target's own page and line shape.

## Yardstick
- **Features:** E032's 13 features, the same yardstick that scored the copy generator (E032, M × 1/3) and the
  per-scribe verbose cipher (E062, C × 1/3), so M and C are judged alike.
- **Score:** z = (target − set mean) / max(sd, 2%|target|, 0.01). A feature fails iff |z| > 3.
- **Unscored:** the E086 lines-independence z is reported for best sets but not scored.
- **Change from what was proposed to Arham:** the proposal said "E093's 12 items"; E032's 13 features are used instead,
  because they already moved both M and C and their rule needs no new thresholds. Disclosed here.

## Known answers first (per class)
- **Planted:** a class-K book (Italian, Voynich-shaped, seed 777, off-grid setting: K1 N 300, K2 sort, K3 r 0.275,
  K4 every 5 lines, K5 first 3 + last sound) must be reproduced by class K's best set (≤ 1 fail).
- **False claim:** the copy generator (E032 output in the Voynich shape) must not be reproduced (best set ≥ 2 fails).
- **Validity:** a class failing either check is VOID for this test.

## Decision table (per valid class, on the Voynich)
| Outcome | Rule | Factor on that class's share |
|---|---|---|
| REPRODUCES | best set ≤ 1 fail, and again ≤ 1 with seeds 11–20 (rule 8) | × 3; class goes to a cracking test |
| CLASS FAILS | every set ≥ 5 fails, and the best set again ≥ 5 with seeds 11–20 | × 1/3 |
| PARTIAL | otherwise, or the seed check disagrees | none |
| VOID | known-answer checks failed | none |

- **C's change:** C × (1 + Σ share × (factor − 1)), then all four renormalised.
- **Range:**
  - all five fail: C × 0.60, i.e. C 0.0998 → about 0.062;
  - all five reproduce: C × 2.20.
- **Honest limit:** this test cannot bring C to 0. Only classes it searches can be excluded, within these settings and
  languages (rule 11).

## Seen beforehand
- **Development (smoke runs):** synthetic targets only (planted books and generator; 2 languages, 3 seeds).
  - With coarse grids (K3 r 0.15/0.30/0.45; K4 line/5 lines/page), the planted K3 and K4 books were not reproduced
    (4 and 3 fails): the grid was too coarse for the planted setting. The grids were made finer (above), after which
    all five planted books were reproduced (0–1 fail) and the generator was not (5–7 fails).
  - No Voynich features were computed during development.
- **Already known from earlier tests:** Voynich's 13 feature values (E062).
- **Built from Voynich data:** the planted targets use the Voynich's unit ranks and common words, as any target does.
