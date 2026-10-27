# E085 pre-registration: do herbal pages showing the same plant share words? (the bridge for picture cribs)

Written 2026-10-27, before the run, at Arham's direction ("go for it", road 1: picture cribs). Script
`experiments/e085_same_plant_pages.py`; output `experiments/results/e085.json`, `e085_run.log`; report
`reports/SAME_PLANT_PAGES.md`.

## Why this test first
E010 showed that the accepted plant identifications (about 6) and the unproven "first word names the plant" link are
too weak to support a crib attack. Before any crib attack, the bridge between picture and text must be shown without
any language: if a page's text is about the plant drawn, two pages drawing the same plant should share vocabulary
(the plant's name, its parts, its uses) more than two random pages do.

## Identifications (fixed before any page text was looked at)
`reports/data/herbal_ids_voynichnu.csv`: 88 DEV herbal pages with a genus from the early identifications collected at
voynich.nu ("herb_oldid": Theodore Petersen's notes, citing O'Neill and Holm; Ethel Voynich's lists). Rule: Ethel
Voynich's genus when given, otherwise Petersen's first named plant; pages with two plants or no genus left out.
Plants on ≥ 2 pages: geranium 4, carduus 4, scabiosa 3, sedum 3, aristolochia, polygonum, botrychium, eryngium, lychnis,
hyoscyamus, primula, artemisia 2 each. Pairs on the same physical sheet are excluded (sheet effect, C24).

## Measure
Page vocabulary = word types among the page's first 200 prose tokens, minus the 100 commonest herbal words. Overlap =
Jaccard. Statistic = mean overlap over same-plant pairs. Null: 10,000 sets of random page pairs, each real pair replaced
by a random pair with the same Currier languages and the same same-quire / different-quire status, not on one sheet,
not same-plant. One-sided p. Secondary (reported): share of same-plant pairs with an identical first word.

## Known answer (validity)
Culpeper's *English Physician* (on disk): 328 herb entries; entries sharing a head noun (Water / Garden Agrimony, the
Cresses, the Thistles, the Mustards...; generic heads TREE, BUSH, GRASS, WOOD, FLOWER, WORT, TONGUE excluded) are
same-kind pairs; same measure (first 200 tokens, minus the 100 commonest words), null = random entry pairs. VALID iff
p < 0.01.

## Decision
| Outcome | Rule | Ledger |
|---|---|---|
| **LINK** | valid; Voynich p < 0.01 | **M × 1/3** (text tracks the pictures); a crib attack using same-plant pages is designed next |
| **NO LINK** | valid; p ≥ 0.01 | **M × 1.4** (a herbal in a language predicts the link if the identifications are partly right; P(link \| L) ≈ 0.3, P(link \| M) ≈ 0.01) |
| VOID | Culpeper fails | none |

## Disclosed
E010 (anchors insufficient), E055 (same-label pharma drawings do not look alike), E073 (zodiac labels: no picture link,
void), C24 (pages on one sheet share vocabulary). The identification table and the Culpeper grouping (with the generic
heads removed after seeing the group list, before any overlap was computed). No overlap has been computed. One attempt.
