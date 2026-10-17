# anchors_v1: sources and dataset notes

Built by `experiments/e010_build_anchors.py`, which writes `anchors.jsonl` (102 rows). The file holds only short
factual items: folio, EVA transliteration from the local ZL3b file, the proposed meaning (a few words), the
proposer and the citation. No prose is copied. Sources were accessed on 2026-10-17 unless stated otherwise.

**This dataset proposes no reading of any Voynich word.** A row records that *someone* proposed a meaning for a
page or a word. It does not record that the proposal is right.

## Row fields
| field | meaning |
|---|---|
| `id`, `anchor_type` | zodiac_month / plant_id / star_label / pharma_label / marginalia |
| `folio`, `leaf`, `section` | from the ZL3b page headers |
| `locked` | leaf is LOCKED_TEST (PROTOCOL_v1 §1): row stored, `usable=false`, excluded from all analyses |
| `tier` | A known script on page · B ≥2 proposers from independent lineages agree (genus level) · C single proposer/lineage or contested · D visual resemblance only (L0) |
| `voynich_side`, `voynich_locus`, `voynich_eva` | which Voynich text the meaning is attached to. Zodiac rows are page-level only (`candidate_labels`, `n_candidate_loci`) |
| `proposers`, `sources`, `contested`, `alternatives` | who proposed it, where, and the competing identifications |
| `verified` | false = a key fact could not be checked against a primary source (see below) |
| `usable`, `word_level` | usable = not locked and not marginalia; word_level = usable and has one Voynich word |

## Counts
| tier | all rows | usable | usable word-level |
|---|---|---|---|
| A | 16 (12 zodiac pages + 4 marginalia) | 12 (zodiac; marginalia are text-only, never usable) | 0 (zodiac rows are page-level: about 15–30 candidate labels each, unknown which, if any, carries the month) |
| B | 6 | 5 (f2r Centaurea, f18r Calendula, f32r Mentha, f90r1 Papaver, f29v Nigella) | 5 |
| C | 79 | 68 | 67 (the f100r pharma row is page-level) |
| D | 1 (f35v ivy, Operation Exemplar L0) | 0 (leaf 35 is LOCKED_TEST) | 0 |

The 14 locked rows are on leaves 1, 8, 9, 30, 35, 38, 51 and 56: f9v Viola (tier B), f1v (Tucker & Talbert),
f35v (tier D), 10 Petersen-lineage plant IDs, and the f1r marginalia. No zodiac leaf (70–73) is locked.

## Sources
- **ZL3b IVTFF** (Zandbergen–Landini, v3b 13/05/2025), local `data/raw/handoff/source_dump/IVTFF Eva.txt.docx`,
  sha256 `6aedc059…ddb7`. Supplies all Voynich label and first-word text, zodiac ring structure, the page
  comments recording 'Mars', 'Abril' and 'May' on f70v2/f70v1/f71v, and 79 '# Plant ID:' comments (Petersen
  lineage, with inline O'Neill / Holm / RZ / Mrs Voynich / Manley tags).
- **R. Zandbergen, voynich.nu**:
  - `https://www.voynich.nu/writing.html` gives the month-name spellings for all 12 pages (mars, aberil,
    aberil, may, may, jong, iollet, augst, septe(m)b(r), octe(m)bre, nove(m)bre, decebre, the last also given as
    "decembre"). He places the language in Northern French ("jong" being the strongest evidence). The same page
    describes the f116v, f66r, f17r and f1r extraneous writing.
  - `https://www.voynich.nu/q10/index.html` and `/q11/index.html`: the month names are written in the centre
    in a different hand, in a version of French. Nymph and label counts per page (f70v2: 29 nymphs + 1 central
    star label; split Aries/Taurus pages: 15 each; f72r2: 30 nymphs, 29 labels). "Each nymph, star and label
    almost certainly refers to one of the 30 degrees" of the sign.
  - `https://voynich.nu/extra/labels.html`: 299 zodiac labels; 80% hapax; the most frequent label word occurs
    5 times (e.g. otaly, okal); ok+ot cover 52% of tokens; 13 types are shared with pharma labels.
  - `https://www.voynich.nu/extra/herb_oldid.html`: old plant identifications (Th. Petersen; Ethel Voynich's
    notebooks at the Grolier Club and the Beinecke; inline O'Neill and Holm). Last updated 2016-12-03.
  - `https://www.voynich.nu/illustr.html`: O'Neill's pepper (f100r) and sunflower IDs, "no longer generally
    accepted". The f35v ivy comparison with BnF Lat. 6823. f68r3 Pleiades.
- **S. Bax (2014)**, "A proposed partial decoding of the Voynich script", v1. The original URL returns 403, so it
  was read via the Wayback Machine copy of
  `https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf`. Rows taken
  from it: f16r juniper (word with 'oror'), f68r Taurus (word next to the Pleiades), f41v coriander (marginal
  word; it cites Sherwood), f2r Centaurea (first word; it cites Sherwood and Velinska), f3v hellebore (cites
  Sherwood), f29v Nigella (cites Sherwood and Velinska), f31r cotton, f27r crocus/'kesar'.
- **E. Sherwood (2013)** and **E. Velinska (2013)**: only as cited by Bax. The primaries were not consulted.
- **A.O. Tucker & R.H. Talbert (2013)**, HerbalGram 100:70–85: only via N. Pelling's summary
  (`https://ciphermysteries.com/2014/01/21/brand-new-new-world-nahuatl-voynich-manuscript-theory`). The f1v
  soap plant (xiuhamolli) row comes from there. The HerbalGram page did not render, and the 37 and later 59
  identifications (Tucker & Janick 2018) were **not collected**.
- **Operation Exemplar** (`external/claude_chat_2026-10-15/FINAL_DISCOVERY_REPORT.md`): f35v ↔ BnF Lat. 6823
  f60r reached only L0 ("weak visual resemblance"), with look-elsewhere p ≈ 1. **No anchor above L0 was found.**
- Background, not stored as rows: forum discussion of the month-name language (French vs Occitan vs Alemannic)
  and of the jong/yony reading (voynich.ninja threads 182 and 4751; stephenbax.net ?p=1226 returned 403).

## Unverified or caveated items (verified=false or noted)
- f68r3 `doaro` as Bax's "Taurus" word. We inferred the locus from his description ("to the right of the seven
  stars") and did not check it against the image.
- f1v Tucker & Talbert: the species-level identification was not seen in the primary source.
- f70v1: the ZL comment spells the month "Abril", voynich.nu has "aberil". Both are stored.
- Which Voynich word (if any) a plant ID belongs to: we use the first word of the page (the Stolfi/Zandbergen
  "first word names the plant" conjecture, never substantiated) unless the proposer named a word. This
  pairing is itself a hypothesis and is the main reason tier B reliability is low (see reports/ANCHORS.md).
- The dating of the month-name hand (15th c.) comes from forum reports of paleographers' opinions and was not
  verified.
- Independence: the Petersen, E. Voynich and ZL-comment lists are one lineage. Sherwood, Velinska and Bax read
  each other. "Multiple proposers agree" is weaker than it looks.
- Plant identifications for f37v–f57 by modern proposers (Sherwood's full list, Velinska, Tucker & Janick)
  were not systematically collected. Their absence lowers the tier B/C counts, but on the evidence in
  reports/ANCHORS.md it would not change the verdict.
