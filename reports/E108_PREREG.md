# E108 pre-registration: gallows shapes by scribe, and calligraphic gallows at word starts (Arham, 2026-10-31)

## Questions
1. **Scribe style.** Do the scribes draw gallows differently? Davis (2020) identified scribes partly by the *k*
   gallows; this is our own measurement.
2. **Calligraphy (Arham).** In Urdu and Arabic calligraphy a letter is drawn stretched and ornate, often at the start.
   Are gallows at the start of a word drawn taller or wider than gallows inside words?
3. **Bench gallows (descriptive).** Is a gallows drawn across *ch* (*cth*, *ckh*) shaped like a plain gallows?

## Images (rule 3)
- 37 single-page canvases at full resolution (2,771 px wide), downloaded 2026-10-31 to
  `data/external/beinecke_hi_e108/` from Yale IIIF. The list is in `data/external/e108_page_list.txt`.
- No LOCKED_TEST leaf and no f102; the script asserts this. Only these images are used.
- **Pages by scribe:**
  - scribe 1: 10 herbal pages;
  - scribe 2: 5 herbal and 6 bathing pages;
  - scribe 3: 10 stars pages;
  - scribe 5: 5 herbal pages and 1 text page.
- Scribe 4 has no usable single-page canvases. Scribe labels and sections come from ZL.

## Procedure (`experiments/e108_gallows_shapes.py`)
### Stage `detect`
- **Detector:** a page-adaptive (Otsu) ink threshold, then connected components.
- **Candidate:** a component 1.8–9 x-heights tall and 0.4–5 wide, sitting on the baseline of ≥ 3 letter-sized
  neighbours and rising ≥ 2.2 x-heights above that baseline.
- **Sample:** up to 40 candidates per page (seed 108108).
- **Stored per candidate:** a crop; features (ascent = height above baseline / x-height; relwidth = width / x-height;
  slant of the principal axis; ink fill; number of enclosed loops); and position.
- **Position:**
  - line-initial: no ink to the left within 6 x-heights on the line;
  - word-initial: gap to the left ink ≥ 0.5 x-height;
  - internal: otherwise.
- Crops are shuffled across all pages into numbered 8 × 6 grids.

### Labelling (blind to page and scribe)
- I (Claude) view each grid and label every cell:
  - **G:** a single gallows standing alone;
  - **B:** a gallows drawn across a *c…h* bench;
  - **M:** a gallows merged with other letters in one blob (shape contaminated);
  - **N:** not a gallows (drawing piece, other letter);
  - **U:** unsure.
- I will not open `records.json` or the page-to-cell mapping while labelling. Labels go to
  `reports/data/e108_labels.csv`, which is committed before `analyze` is run.

### Stage `analyze`
**Scribes**
- Use G gallows only, with page means over pages that have ≥ 5 G.
- **Classifier:** leave-one-page-out nearest-centroid classification of pages into scribes on the 5 standardised
  features. Permutation p uses 1,000 shuffles of scribe labels across pages.
- **Validity:** each of scribes 1, 2, 3 and 5 has ≥ 4 pages and ≥ 15 G.

| Outcome | Rule |
|---|---|
| SCRIBES DIFFER | p < 0.01 (all pages) |
| WEAK | 0.01 ≤ p < 0.05 |
| NO DIFFERENCE SHOWN | p ≥ 0.05 |
| VOID | invalid |

- **Secondary:** herbal pages only (scribes 1, 2, 5), which holds section fixed. Scribe 3 is stars only, so the
  all-pages test mixes scribe with section; this is a disclosed limitation.

**Position (calligraphy)**
- For pages with ≥ 3 word-initial and ≥ 3 internal G, compute the per-page relative difference
  (mean word-initial / mean internal − 1) for ascent and relwidth.
- One-sided Wilcoxon signed-rank test across pages; at least 8 pages are needed, otherwise VOID.

| Outcome | Rule |
|---|---|
| DECORATED AT WORD START | for ascent or relwidth, p < 0.005 (Bonferroni over 2) and median increase ≥ 10% |
| NOT LARGER AT WORD START | otherwise |

- **Unscored:** line-initial vs internal (this includes paragraph-initial gallows, which are known to be large).

**Bench (descriptive):** mean ascent, relwidth and loops of B against G.

**No Bayes factors.** Letter style fits M, L and C alike.

## Seen beforehand
- Detector tuning was done by eye on f103r, f2r and f78r. Plant-drawing pieces are detected on herbal pages, which is
  why every candidate is labelled. Candidate counts per page range from 9 (scribe 1 herbal) to 282 (stars).
- **Smoke run** on a scratch copy (5 pages, *random* fake labels):
  - candidate feature means by scribe: ascent about 3.1–3.2, relwidth about 2.5, slant −15 to −20, loops 0.6–0.8;
  - line-initial candidates about 80% taller and 50% wider than internal ones.
- E106 (paragraph gallows DECORATIVE, marginal), E107 (gallows pairs PARTLY), Davis 2020, Timm's critique (44 pages).
