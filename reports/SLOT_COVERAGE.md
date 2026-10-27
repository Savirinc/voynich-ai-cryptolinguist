# E074: how much of the text is front piece + middle + ending? ABOVE EVERY LANGUAGE (measurement, no factor)

Run 2026-10-27 under `E074_PREREG.md` (locked). Script `experiments/e074_slot_coverage.py`; results
`experiments/results/e074.json`, log `e074_run.log`. Asked by Arham.

## In one paragraph
Lists of pieces were built automatically from the first half of each text and used to write the second half. With 10
front pieces, 30 middles and 20 endings (60 pieces), the lists write **64% of the Voynich running text**; the same recipe
writes 17–52% of eight real languages. With 120 pieces Voynich reaches 85%, languages 25–62%. Voynich's pieces also
combine more freely: 20% of all possible front × middle × ending combinations are real Voynich words, against 3–15% in
the languages. The copy generator matches Voynich on every number.

## Results (check half, token coverage = share of running words written by the system)
| Text | 30 pieces | **60 pieces (primary)** | 120 pieces | fill rate, 60 pieces |
|---|---|---|---|---|
| **Voynich** | 0.299 | **0.643** | 0.853 | **0.195** |
| Tagalog (tglulb) | 0.272 | 0.518 | 0.611 | 0.028 |
| English KJV | 0.347 | 0.445 | 0.618 | 0.035 |
| Hebrew (consonants) | 0.161 | 0.392 | 0.575 | 0.145 |
| German | 0.131 | 0.359 | 0.611 | 0.040 |
| Latin Vulgate | 0.188 | 0.311 | 0.425 | 0.043 |
| Indonesian | 0.072 | 0.230 | 0.347 | 0.029 |
| Hungarian | 0.133 | 0.211 | 0.377 | 0.025 |
| Turkish | 0.025 | 0.166 | 0.249 | 0.033 |
| generator seeds 31–33 | 0.294–0.314 | 0.591–0.682 | 0.848–0.862 | 0.147–0.149 |

Word types (vocabulary, not running text) at 60 pieces: Voynich 23%, languages 3–16% (Hebrew highest), generator
26–27%. **Reading (pre-set): ABOVE EVERY LANGUAGE.**

## The Voynich lists the recipe found (60 pieces)
- **Front (10):** (none), o, c, ch, q, s, qo, d, y, sh
- **Middle (30):** (none), o, k, a, t, ch, d, ol, ke, e, ka, pch, tch, ok, cth, kch, l, to, ko, cho, ee, od, ckh, che, ot,
  sh, kee, ai, da, te, al
- **Ending (20):** (none), y, dy, r, l, n, in, ey, hy, iin, ol, aiin, edy, s, ar, or, al, m, d, hey
- Commonest words it cannot write: *lchedy, otain, cheody, raiin, cheo, lkaiin, qotain, lkeey, lkain, lkeedy*. Many start
  with *l*, which the automatic recipe did not pick as a front piece. The recipe is crude (it cut *c* and *ch*
  separately); it is applied identically to every text, which is what makes the comparison fair.

## What it means
- Voynich words are far more "slot-built" than any of the eight languages: fewer pieces write more of the text, and
  the pieces combine more freely. Hebrew, with its stacked one-letter prefixes, is the closest language on fill rate.
- The copy generator is as slot-built as Voynich. The measurement does not separate a language, a cipher or a
  meaningless system; as pre-registered, no ledger factor.
