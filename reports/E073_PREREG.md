# E073 pre-registration: do zodiac figures with the same label look alike? (title + name reading)

Written 2026-10-27, before any figure is annotated. Script: `experiments/e073_zodiac_attributes.py`. Annotations:
`experiments/results/e073_annotations.json` (primary), `e073_annotations_check.json` (independent second annotator).
Output `experiments/results/e073.json`, `e073_run.log`, report `reports/ZODIAC_ATTRIBUTES.md`. Updates `LEDGER.md`.

## Question
Label-class reading 2 says a zodiac label is a title or name: front piece *ot/ok* (E072: one detachable piece) plus a
name. If the names (or titles) refer to kinds of figure, figures with the same label should share visible features
more than figures with different labels, beyond what their page and ring already explain. Do they?

## Data
- **Images:** Beinecke IIIF canvases 1006200–1006207 (full size): f70v2, f70v1, f71r, f71v and f72r1–3, f72v1–3,
  f73r, f73v. All on leaves 70–73 (DEV); none shares a canvas with a LOCKED_TEST page.
- **Labels:** ZL 3b nymph labels (locus type L) on the 12 zodiac pages, with the transcriber's clock position (comment
  `<!hh:mm>`, "clock position is that of nymph") and ring heading, normalised to top / outer / middle (second, middle,
  and the f72r2 renumbering note) / inner. Label text: first alternative of `[a:b]`, braces and separators removed;
  labels containing `?` or without a clock position are dropped. Design count: 299 labels, 251 types, 31 types
  repeated, 77 same-label pairs (66 across pages); 1 label lacks a clock.

## Annotation (blind to labels)
Each figure is recorded by page, ring and clock position (12 = top of the page as photographed), with five features;
a feature that cannot be judged is `?` and is skipped in comparisons:
| Feature | Values |
|---|---|
| BARREL | 1 if the figure stands in or beside a tub/barrel, else 0 |
| CLOTHED | 1 if the body is covered by a garment, else 0 |
| HEAD | 1 if any head covering (crown, cap, hat, veil, hood), else 0 |
| HANDSTAR | 1 if a hand holds or touches the star or its string, else 0 |
| FACING | L / R / F: head turned to the viewer's left, right, or frontal |
The primary annotation is done by Claude from crops of the full-size images, page by page, without opening the label
list during annotation. A second, independent annotator (a fresh subagent given only this protocol and the crops)
annotates three pages chosen by `random.Random(73).sample(pages, 3)`.

## Joining figures to labels
Within each (page, ring): if the number of annotated figures equals the number of labels, both are sorted by clock angle
and joined by the cyclic shift that minimises total angular distance; otherwise by minimum-cost assignment
(`linear_sum_assignment`) on angular distance. Joined pairs more than 45° apart are dropped. The share joined and the
mean angular error are reported.

## Statistic
For a set of figure pairs, SIM = mean over pairs of the share of features (both values known) that are equal.
Primary: **same-label pairs** (identical label text). Control: labels shuffled among the joined figures **within each
(page, ring)**, 2,000 shuffles × 10 seeds (73,001–73,010); z = (SIM − mean) / sd; median z; a side holds if ≥ 8 of 10
seeds agree. Reported, not scored: pairs sharing the remainder after *ot/ok/op/of* (with *ot* = *ok*, E072); per-feature
agreement; same-label pairs across pages only.

## Validity checks (all before the primary statistic is read)
1. **Known answer from the transcriber's page notes** (ZL comments): f72r1 inner ring in barrels, outer ring standing
   without barrels; f71v outer ring 10 figures in barrels, inner ring 5 figures of which one naked and four clothed;
   f70v2 inner ring figures beside a barrel. The primary annotation must agree on ≥ 90% of these figure-level calls.
2. **Reliability:** Cohen's kappa between the two annotators on the three check pages, per feature. A feature with
   kappa < 0.5 is dropped from SIM (FACING uses three-valued kappa). If fewer than three features survive: VOID.
3. **Join quality:** ≥ 85% of labels joined with mean angular error ≤ 20°. Otherwise VOID.

## Decision table
| Outcome | Rule | Ledger |
|---|---|---|
| **PICTURE LINK** | same-label z > 3 (8/10 seeds) | **M × 1/3** (labels track what is drawn: a meaning link) |
| **NO LINK** | z ≤ 3 (8/10 seeds) | **M × 1.5** (a meaningless label system predicts no link; under L about a third of label readings predict one: P(link\|L) ≈ 0.35, P(link\|M) ≈ 0.05, so no link gives 0.65 / 0.95 ≈ 1/1.5) |
| INCONCLUSIVE | seeds split | none |
| VOID | any validity check fails | none |
Why not more for a link: a deliberate hoaxer could also give the same label to similar figures, and E055 found no such
link for pharma drawings; × 3 matches the other weak factors.

## Disclosed (seen beforehand)
- Design counts above; the raw f73r transcription (labels with clock positions) was printed while locating ring
  information; thumbnails of all canvases and a 1,300-pixel view of f73r were viewed to choose the five features.
- E055: same-label pharma drawings do not look alike. Step 0, E071, E072 results.
- 2026-10-25 descriptive fact: repeated zodiac labels do not sit at the same ring position.
- No figure has been annotated; no figure has been joined to a label.
- One attempt (rule 9). The script is exercised on fabricated annotations before locking.
- The script's own label cleaning keeps whole labels and drops `?`: 293 labels and 49 same-label pairs (the design
  count above used first words). Fabricated annotations: planted link z +16, random features z −1.0, join share 1.00,
  mean angular error 4°.
