# E075: does swapping a word piece change the word's job the same way every time? BETWEEN (no factor)

Run 2026-10-27 under `E075_PREREG.md` (locked). Script `experiments/e075_piece_effects.py`; results
`experiments/results/e075.json`, log `e075_run.log`. Asked by Arham (assume a language; see what the pieces do).

## In one paragraph
For every swap of one piece (X → oX, Xdy → Xy, ...) the change in the word's neighbours was measured across many cores.
The method finds real grammar where it exists: Hebrew *ve-* "and", *ha-* "the", *-o* "his", *vay-* (narrative verb),
*le-* "to"; Latin case endings *-i / -o / -um / -s*, including Latin's agreement between neighbouring endings. Shuffled
texts give nothing. On Voynich, 93 of 117 swaps (79%) shift the word's neighbours consistently, far more than any
language (0–50%), but the copy generator also scores 57–76%. Voynich is above the generator's best by 0.04, short of
the pre-set margin of 0.05: BETWEEN, no factor.

## Results
| Text | eligible swaps | consistent (z > 3) | share |
|---|---|---|---|
| **Voynich** | 117 | 93 | **0.795** |
| Latin (latVUC) | 33 | 12 | 0.364 |
| German | 28 | 9 | 0.321 |
| Hebrew (consonants) | 43 | 9 | 0.209 |
| Indonesian | 8 | 4 | 0.500 |
| English KJV | 6 | 1 | 0.167 |
| Turkish | 19 | 0 | 0.000 |
| generator 31 / 32 / 33 | 112 / 107 / 107 | 85 / 74 / 61 | 0.759 / 0.692 / 0.570 |
| shuffled Voynich, Hebrew, Latin | 117 / 43 / 33 | 0 | 0.000 |

VALID (Hebrew 9, Latin 12 consistent; shuffled 0). **Verdict: BETWEEN** (0.795 vs generator maximum 0.759 + 0.05).

## What the Voynich pieces do (strongest consistent swaps; no meaning implied)
| Swap | cores | z | what changes |
|---|---|---|---|
| X → qoX, X → qX, oX → qoX | 82–86 | +9.5 to +12.1 | the word now follows a word ending *-edy* (junction rule, E059) |
| Xdy → Xy, Xedy → Xey, Xedy → Xy | 52–88 | +8.3 to +11.4 | the *-dy/-edy* form sits among other *-edy* words and before *qo-* words: neighbouring endings agree |
| Xol, Xor, Xar, Xal, Xaiin → Xy | 36–61 | +5.7 to +8.5 | the *-y* form is more often last in the line |
| Xl, Xr, Xiin → Xm | 21–27 | +4.4 to +5.0 | the *-m* form is last in the line (about 0.5–0.6 more often) |
| X → dX, sX, yX, oX→yX | 16–57 | +3.5 to +7.3 | the new form is more often first in the line |
| chX → shX | 57 | +8.2 | the *sh-* form is followed more often by a *qo-* word |
| Xl → Xr, Xaiin → Xar | 34–79 | +6.4 to +7.9 | small, consistent shifts in the next word's front |

For comparison, Hebrew's strongest: X → *ve*X (89 cores, z +7.5), X → X*o* "his" (+5.2), X → *ha*X (+4.9), X → *vay*X (+4.9).
Latin's strongest: *agri* → *agro* type (-i → -o, +5.4: the -o form follows another -o word, case agreement), -o → -um
(+4.7), -m → -s (+4.6).

## Reading
- Voynich's pieces have jobs in the sense measured here: three kinds stand out. **Line-position pieces** (*d-, s-, y-*
  at line start; *-m, -y* at line end), **a junction piece** (*q-* after *-edy*), and **agreement** (*-edy* words keep
  company with other *-edy* words, as Latin *-o* words do with *-o* words).
- The copy generator produces almost as many consistent swaps, because copying a nearby word and changing one piece
  keeps neighbouring words alike and inherits the line-position habits it copies. So these jobs are what a language's
  grammar would give, and also what copy-and-change gives. The test does not separate them; as pre-registered, no
  factor.
- Languages score lower partly because an automatic kit of first letters and last letters cuts most of their words at
  meaningless places; their consistent swaps are the real grammar pieces.
