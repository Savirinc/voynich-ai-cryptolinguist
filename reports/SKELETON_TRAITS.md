# E078: Voynich's word skeleton counted, and which languages share it (descriptive, no factor)

Run 2026-10-27 under `E078_PREREG.md` (locked). Script `experiments/e078_skeleton_traits.py`; results
`experiments/results/e078.json`, log `e078_run.log`. Arham's option 1.

## Voynich's skeleton against 62 languages
| Trait | Voynich | languages (range) | Voynich higher than |
|---|---|---|---|
| productive fronts | 8 | 0–10 | 60 of 62 |
| productive endings | 20 (all 20 listed) | 5–20 | 61 of 62 |
| bound bridges (bridge not a word alone) | 0.41 | 0.33–0.99 | 1 of 62 |
| free endings (productive endings that are also words) | 0.60 | 0–1 | 57 of 62 |
| bare endings (share of running words) | 0.092 | 0–0.41 | 40 of 62 |
| fill rate | 0.204 | 0.018–0.150 | 62 of 62 |

## Closest languages (scaled distance)
| Rank | Text | distance | fronts | endings | bound | free endings | bare | fill |
|---|---|---|---|---|---|---|---|---|
| — | **Voynich** | — | 8 | 20 | 0.41 | 0.60 | 0.092 | 0.204 |
| 1 | **Hebrew** | 4.54 | 8 | 20 | 0.80 | 0.00 | 0.000 | 0.150 |
| 2 | **Urdu** | 5.11 | 10 | 14 | 0.33 | 0.64 | 0.241 | 0.106 |
| 3 | bqcsim (Boko, Benin) | 6.05 | 0 | 19 | 0.46 | 0.53 | 0.072 | 0.102 |
| 4 | Luo | 6.10 | 6 | 17 | 0.72 | 0.35 | 0.089 | 0.080 |
| 5 | **Arabic** | 6.33 | 5 | 18 | 0.77 | 0.17 | 0.006 | 0.086 |
| 8 | **Persian** | 7.16 | 2 | 18 | 0.74 | 0.22 | 0.093 | 0.071 |
| 32 | Latin | 8.84 | 0 | 16 | 0.83 | 0.19 | 0.004 | 0.045 |
| 50 | English | 9.48 | 0 | 9 | 0.69 | 0.00 | 0.000 | 0.035 |
| — | generator 31 / 32 / 33 | 3.30 / 3.60 / 3.77 | 7 | 19–20 | 0.80–0.86 | 0.50–0.58 | 0.083–0.105 | 0.15–0.16 |

## Reading
- Only languages with many front pieces come near: Hebrew matches Voynich exactly on productive fronts (8) and endings
  (20); Urdu matches on free and bare endings (its postpositions *ka, ki, ko, se, ne* stand alone). Four of the eight
  closest are written in Hebrew or Arabic script (Hebrew, Urdu, Arabic, Persian). Latin, Romance, Germanic and English
  are far.
- No language has Voynich's whole skeleton: Hebrew has no free or bare endings; Urdu has fewer productive endings.
- The copy generator is closer to Voynich (3.3–3.8) than any language (Hebrew 4.5). The skeleton is what a
  copy-and-change process makes from Voynich-like seed words, so it does not separate a language from meaningless
  text.
- Correction to the working model: BOUND is low (0.41) because many Voynich bridges are single glyphs (*o, l, r, d, s,
  y*) that also occur as one-glyph words; the multi-glyph bridges (*k, ke, te, tch, ckh, pch*) are almost never words
  alone (2026-10-27 count).
- No ledger factor (descriptive, working assumption L).
