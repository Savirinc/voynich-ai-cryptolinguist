# E073: do zodiac figures with the same label look alike? VOID (reliability check), unscored lean: no link

Run 2026-10-27 under `E073_PREREG.md` (locked; commit ee4c0d1). Script `experiments/e073_zodiac_attributes.py`;
annotations `experiments/results/e073_annotations.json` (Claude, 296 figures on 12 pages) and
`e073_annotations_check.json` (independent subagent, 74 figures on f72r1, f70v2, f72v2); results `e073.json`, log
`e073_run.log`. Images: Beinecke canvases 1006200–1006207 (leaves 70–73, DEV), downloaded to
`data/external/beinecke_images/zodiac/` (gitignored).

## Validity checks
| Check | Bar | Result |
|---|---|---|
| 1. Transcriber's page notes (barrels on f72r1 inner, f71v outer, f70v2 inner; none on f72r1 outer; f71v inner 1 naked + 4 clothed) | ≥ 90% | **100%** (40 calls) |
| 2. Second-annotator kappa, per feature; ≥ 3 features with kappa ≥ 0.5 | 3 features | **2 kept** (BARREL 0.75, HEAD 0.71); CLOTHED 0.00, HANDSTAR 0.32, FACING 0.13 |
| 3. Join of figures to labels | ≥ 85%, ≤ 20° | 291 of 293 (99%), mean error 6.5° |

**Verdict: VOID** (check 2). No ledger factor.

## What went wrong in check 2 (stated plainly)
| Feature | Figures both judged | Raw agreement | kappa |
|---|---|---|---|
| BARREL | 49 | 0.90 | 0.75 |
| CLOTHED | 62 | **0.98** | **0.00** |
| HEAD | 63 | 0.94 | 0.71 |
| HANDSTAR | 45 | 0.62 | 0.32 |
| FACING | 65 | 0.68 | 0.13 |
CLOTHED failed by a known flaw of kappa, not by disagreement: on the three randomly chosen check pages almost every
figure is naked (61 of 62 agreed "naked"; one disagreement), so kappa cannot rise above zero. The pre-registration did
not anticipate a near-constant feature. HANDSTAR and FACING genuinely disagree (the second annotator saw more hands
touching stars and more turned heads). Because the primary statistic was printed in the same run, the rule is **not**
amended after the fact; a future attempt would need a new pre-registration (for example raw agreement ≥ 0.85 when one
value exceeds 90%, and check pages drawn to include clothed figures).

## Unscored numbers (computed on BARREL, CLOTHED, HEAD, HANDSTAR, FACING, the script's fallback when < 3 features pass)
| Pairs | n | similarity | z vs within-page/ring label shuffles |
|---|---|---|---|
| same label | 49 | 0.815 | −0.20 (0/10 seeds > 3) |
| same label, different pages | 42 | 0.802 | −0.19 |
| same remainder after ot/ok/op/of | 110 | 0.786 | −0.85 |
| per feature, same label | 24–49 | | −1.27 to +1.24 |
Every number sits at chance. Had CLOTHED been kept, three features would pass and the pre-set rule would read NO LINK
(M × 1.5); this is recorded as an unscored lean, not applied.

## Reading
Figures that carry the same label do not share barrels, clothing, head coverings, star-holding or facing more than
figures with different labels on the same page and ring. This repeats E055 (same-label pharma drawings do not look
alike) on a second picture type. Limits: page and ring explain most of what varies (barrels and clothing are page
habits), so the visible features leave little room inside a page; many faint figures were scored "?".

## For the label-class programme
All five readings have now been tried. List words (step 0), abbreviations (E071), quantities (E056, step 0) and
category + identifier are weakened; the front piece is detachable but generator-like (E072); title + name has no
visible support (E073 VOID, lean no link). The label class is real as a shape (o + tall letter + common word) but no
test so far ties it to meaning.
