# E022 pre-registration: methodology test A2b — do plants that look alike have pages with alike words?

Written 2026-10-18, BEFORE any image was viewed or coded and before any text similarity was computed.

## Why this test
A meaningful herbal repeats a plant's name and properties wherever that plant (or a similar one) is described.
Copying-based gibberish (Timm & Schinner) and grille generators link text only to nearby text, never to what a
distant page's drawing looks like. One plant per herbal page links each page's text to its picture without
reading glyph positions.

## Pages
Voynich herbal pages (illustration H) on DEV leaves: 110 pages; excluded in advance: the 9 foldout panels f90r1,
f90r2, f90v1, f90v2, f95r1, f95r2, f95v1, f95v2 (several plants per image) and f94v (no single canvas in the
Beinecke manifest) → 101 pages. Images: Beinecke MS 408 IIIF (collections.library.yale.edu/manifests/2002046).
LOCKED_TEST leaves are neither viewed nor used.

## Visual coding (done first, from images only, then locked by sha256 before any text comparison)
Coder: Claude, viewing each page image; the text on the page is not read or transcribed during coding, and no text
statistic exists before the codes are locked. 13 categorical features of the main plant drawing:
1 root: none_small / bulb_tuber / taproot / branched_fibrous / other
2 stems: one / two / three_plus
3 leaf_arrangement: basal / alternate / opposite / clustered_whorled / unclear
4 leaf_shape: round_oval / long_narrow / lobed_divided / compound_leaflets / grass_needle / mixed
5 leaf_margin: smooth / toothed / wavy_lobed / unclear
6 leaf_count: few_large / many_small / medium
7 flower: none / single / several / head_cluster / spike
8 flower_color: none / blue / red_pink / yellow_brown / white_other / multi
9 fruit_or_pods: yes / no
10 leaf_color: green / blue_green / brown_yellow / multi
11 symmetry: symmetric / asymmetric
12 height: small / medium / tall
13 thorns_hairs: yes / no
Visual similarity of two pages = share of features that match, ignoring features coded unclear on either page.

## Text similarity
Page prose word types (EVA, clean tokens). tf-idf over the 101 pages, restricted to types occurring on 2–15 of
the pages (content-like types; the most widespread types excluded). Text similarity = cosine.

## Statistic and decision (fixed now)
- Pairs: all page pairs at least 4 folio numbers apart (removes adjacency: same sitting, same bifolio).
- Statistic: Spearman correlation r between visual and text similarity over those pairs.
- Null: 10,000 permutations of the visual codes among pages within the same stratum (Currier language × hand),
  so scribe and dialect effects are kept in the null. One-sided p = share of permutations with r >= observed.
- MEANING LINK DETECTED iff p < 0.01. Otherwise NOT DETECTED.
- Reported, no decision: r and p using all pairs; within Currier A hand 1 only; first-word sharing rate among the
  10% most visually similar pairs vs the rest.

## What this cannot show
- NOT DETECTED does not prove meaninglessness. The plants may be stylised or fanciful, a page's text may not
  describe its plant, or the coding may be too coarse (low power).
- DETECTED shows the text tracks the pictures across distant pages, which is strong evidence against copying- or
  grille-type gibberish. It is not a reading.
- There is one coder (no inter-rater check).
