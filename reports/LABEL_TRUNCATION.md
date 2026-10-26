# E071: are the label words truncations of longer words? NOT ABBREVIATION-LIKE

Run 2026-10-26 under `E071_PREREG.md` (locked; prereg sha256 b806d061…, script sha256 91cbbc16…). Script
`experiments/e071_label_truncation.py`; results `experiments/results/e071.json`, log `e071_run.log`. Runtime 8 s.

## In one paragraph
If the label words were shortened forms of longer words that also appear in full ("op" for opus), each label word
should be the beginning of longer text words more often than an ordinary word of the same length and commonness. The
measure finds real shortenings every time it is shown them (Gaskell & Bowern's abbreviated Pliny z +14 to +16; planted
truncations in Latin, German, Turkish z +12 to +21) and claims nothing on random words (nine control sets, z −1.6 to
+0.7). On Voynich, the 95 o-tall-letter label words score like matched ordinary words (z +0.44 general, +0.52 against
their own class); all 280 label words score z +0.04. Labels are not truncations. Within L, the abbreviation form loses
share (L-abbrev × 0.6); M, L, C unchanged.

## Validation (before Voynich)
| Text | Target set | n | z (median of 10 seeds) | rule |
|---|---|---|---|---|
| Pliny abbreviated (G&B), window 0 | truncation types | 106 | +14.19 (10/10 > 3) | pass |
| Pliny abbreviated, window 100,000 | truncation types | 109 | +16.31 (10/10) | pass |
| Pliny abbreviated, window 200,000 | truncation types | 99 | +14.84 (10/10) | pass |
| latVUC, planted | cut forms | 126 | +20.86 (10/10) | pass |
| deu1912, planted | cut forms | 122 | +14.68 (10/10) | pass |
| turytc, planted | cut forms | 122 | +12.07 (10/10) | pass |
| the same six texts | matched pseudo-labels | 99–126 | −1.63 to +0.11 (10/10 within ±3) | pass |
| generator seeds 31–33 | 95 random words | 95 | −0.16 to +0.70 (10/10 within) | pass |

Known answers 6/6, false claims 9/9: VALID. The aligned Pliny stream has 404,967 token pairs.

## Voynich
| Set | n | prefix score S | z | seeds > 3 | commonest-extension share |
|---|---|---|---|---|---|
| T1: o-gallows label words vs all matched non-label words | 95 | 1.034 | **+0.44** | 0/10 | 0.59 |
| T1 vs matched non-label o-gallows words (class-internal) | 95 | 1.034 | +0.52 | 0/10 | |
| T2: all label words vs matched non-label words | 280 | 1.459 | +0.04 | 0/10 | 0.48 |

Detail: 49 of the 95 o-gallows label words have no extension at all; the most extended are `oto` (35 extensions), `oko`
(25), `otal` (25), `okal` (22), `oteo` (20), which are short stems with the usual endings, not shortened long words.
Where extensions exist, the commonest one takes 0.59 of extension tokens (Pliny truncations 0.20–0.28; planted
truncations 0.40–0.62), so the top-extension share does not separate the cases and is recorded only.

## Verdict and ledger
**NOT ABBREVIATION-LIKE** (T1 z ≤ 3 in 10/10 seeds). Absence rule, as pre-registered: the "suspensions of words also
written in full" form is s = 0.5 of L-abbrev, m = 0.2 → **L-abbrev × 0.6**. Forms of L renormalised: L-unattested
0.35, L-syll 0.21, L-abbrev 0.12, L-other 0.17, L-alpha-known 0.15. M, L, C, O unchanged. A word that is *always*
abbreviated leaves no full form and is outside this test's scope.

## For the label-class programme
Reading 3 (abbreviated phrases) is now weakened by a validated search. With reading 1 set aside by step 0 and readings
4 and 5 weakened earlier, reading 2 (title + name, cores recurring on the same kind of thing) is the one still
standing with an untested prediction. It needs the zodiac images (E072 candidate).
