# E076: light (antonym/synonym-type) versus heavy (grammar) pieces, and which languages are closest. VALID; no factor

Run 2026-10-27 under `E076_PREREG.md` (locked). Script `experiments/e076_light_heavy_pieces.py`; results
`experiments/results/e076.json`, log `e076_run.log`. Asked by Arham; copy generator left out at his direction, so no
ledger factor.

## Known answers (antonym pieces must come out light)
| Piece | pairs | median lightness | examples |
|---|---|---|---|
| English *un-* | 24 | **0.91** | clean/unclean, righteous/unrighteous, leavened/unleavened |
| German *un-* | 40 | **0.92** | rein/unrein, möglich/unmöglich, recht/unrecht |
| Persian *nā-* | 16 | 0.75 (medium; includes non-antonyms such as the name Nāhor) | pāk/nāpāk, pasand/nāpasand, mokhtun/nāmokhtun |
Random word pairs: 0.47–0.53. **VALID.** Antonym pieces keep a word in the same places, as expected.

## Voynich profile
117 eligible swaps: **light 62%**, medium 21%, heavy 17%; consistent 81%; front pieces are 21% of light swaps, 35% of
heavy swaps.

| Class | Voynich swaps (lightness) |
|---|---|
| **Light** (72): the new form sits where the old one sits | *d- ↔ y-* (0.99: dchedy/ychedy), *d- ↔ s-* (0.98: daiin/saiin), *-s ↔ -y* (0.98), *-al ↔ -y* (0.96), *-iin ↔ -in* (0.96: aiin/ain), *-r ↔ -s* (0.96), *-ol ↔ -or* (0.96), *-dy ↔ -edy* (0.96: chdy/chedy), *-l ↔ -r* (0.94: al/ar), *-o ↔ -y* (0.94: cheo/chey), *-n ↔ -r* (0.94: ain/air) |
| **Medium** (25) | *-edy ↔ -y*, *-edy ↔ -ol* (chedy/chol), *X ↔ chX* (aiin/chaiin), *X ↔ X-aiin*, *X ↔ X-ol* |
| **Heavy** (20): the new form moves elsewhere | *-aiin ↔ -dy* (chaiin/chdy), *X ↔ dX*, *X ↔ yX*, *ch- ↔ y-*, *q- ↔ sh-*, *o- ↔ sh-*, *-edy ↔ -o* (chedy/cho), *X ↔ X-d* |

## Comparison with languages (28,841 tokens each, Voynich line lengths)
| Text | light | medium | heavy | consistent |
|---|---|---|---|---|
| **Voynich** (117 swaps) | **0.62** | 0.21 | 0.17 | **0.81** |
| Assamese (18) | 0.61 | 0.22 | 0.17 | 0.67 |
| Uyghur, Arabic script (17) | 0.59 | 0.29 | 0.12 | 0.47 |
| Persian (26) | 0.42 | 0.19 | 0.38 | 0.15 |
| German (28) | 0.32 | 0.32 | 0.36 | 0.32 |
| Hebrew (43) | 0.30 | 0.42 | 0.28 | 0.21 |
| Arabic (34) | 0.29 | 0.50 | 0.21 | 0.24 |
| Latin (33) | 0.09 | 0.58 | 0.33 | 0.33 |
| Urdu (50) | 0.06 | 0.32 | 0.62 | 0.04 |

Closest profiles (distance): Assamese 0.43, Uyghur 0.50, Tamil 0.63, Panjabi 0.65, German 0.70, Lithuanian 0.73,
Romani 0.73, Persian 0.76, Swahili 0.76, Oromo 0.77, Hebrew 0.78, Arabic 0.78. Farthest: Polish 1.28, Romanian 1.20,
Cebuano 1.18, Italian 1.17, Māori 1.11. 41 texts ranked; 19 had fewer than 10 eligible swaps and were not ranked.

## Reading
- Most Voynich piece swaps are light: changing *d-* to *s-* or *y-*, *-l* to *-r*, *-ol* to *-or*, *-iin* to *-in*,
  *-dy* to *-edy* keeps the word in the same places. These are where antonym- or synonym-type pieces would be, but a
  light swap is equally what a spelling variant gives (E038 found *e/ee* to be one sign); the method cannot tell those
  three apart.
- Voynich has more light swaps than all but two languages and more consistent swaps than any.
- No language is close in absolute terms; the nearest (Assamese, Uyghur, Tamil, Panjabi) rest on 10–18 swaps each,
  so the ranking is noisy. Hebrew, Arabic and Persian sit in the middle of the ranking; Latin and the Romance languages
  are among the farthest.
- No ledger factor (generator not run, at Arham's direction).
