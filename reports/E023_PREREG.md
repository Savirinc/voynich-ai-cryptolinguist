# E023 pre-registration: power check for the E022 plant–text test, on a real herbal

Written 2026-10-18, BEFORE any coding or text similarity. Methodology rule 9: a meaning test needs a positive
control before its null can be read.

## Material
Culpeper, *The Complete Herbal* (Project Gutenberg #49513). Entries with both a `_Descript._` (appearance) and a
`_Government and virtues._` (astrology, medical uses) section: 205. A seeded random sample (seed 23023) of 101
entries, kept in the book's order: data/derived/e023/culpeper_sample.json.

## Analogue of E022
- **"Picture":** the Descript. section stands in for the drawing. A blind coder agent reads ONLY the descriptions
  (data/derived/e023/descriptions_only.json: ids and description text, no names, no virtues) and codes the same 13
  visual features, with the same allowed values and rules as E022. The codes are locked read-only before any text
  comparison.
- **"Page text":** the Government and virtues section only. No description and no names, so appearance words can't
  leak in (a medieval herbal page mostly gives uses).
- **Statistic:** identical to E022.
  - tf-idf over virtues word types (lowercase, letters only) occurring on 2–15 entries; cosine similarity.
  - Spearman r between visual similarity (share of matching features, unclear ignored) and text similarity, over
    pairs at least 4 entries apart in book order.
  - 10,000 permutations of the visual codes over entries (one stratum: one author, one hand). One-sided p.

## Decision (fixed now)
- POWER SHOWN iff p < 0.01. Then E022's NOT DETECTED becomes informative: a real herbal's use-text tracks its plants'
  appearance under this test, Voynich's doesn't.
- Otherwise NO POWER: the plant–text test cannot detect meaning in herbal-type text. E022 is uninformative, and
  this line is dropped.
- Reported: r and p with the intro paragraph (alternative plant names) added to the text.

## Limits
English, 1653, printed and written by one author; the descriptions are verbal, not stylised drawings. The visual
codes from descriptions are probably cleaner than codes from Voynich drawings, so POWER SHOWN is an upper bound on
the power E022 had.
