# E103 pre-registration: section-by-section vocabulary drift, confirmatory (Arham, 2026-10-31)

## Question
After E102 (VOID), an unscored pattern turned up. In the three compact sections (bathing B scribe 2, stars B scribe 3,
pharma A scribe 1), meaningful texts usually drift: near pages share more vocabulary than far pages. The copy generator
and Naibbe do not drift there, and neither did the Voynich (−0.03, +0.04, −0.07). Is this pattern real, and does it
survive other transcriptions and another similarity measure?

## Why this design (the pattern was seen first)
The ZL cosine numbers are already known. A test on them alone would be circular. Three things guard against that:
- **Three of four variants are new measurements:**
  - V2: ZL with Jaccard similarity of word types;
  - V3: the Takahashi transcription (own readings and spaces);
  - V4: Glen Claston (a different glyph cut and different spaces).
- **The verdict needs agreement in every valid variant,** with at least 3 of the 4 valid.
- **The factors are reduced** to × 2 / × 1/2, from the × 3 / × 1/3 used for unseen tests.

## Data and procedure (`experiments/e103_section_drift.py`)
- **Pages and pairs as E102:** same Currier language, scribe and section; different sheets; pages ≥ 60 clean tokens;
  groups ≥ 5 pages. Page metadata comes from ZL. LOCKED_TEST leaves are excluded.
- **Statistic:** COMPACT = mean of the group DRIFT values (−Spearman ρ of similarity against page distance) over the
  three compact sections. The sections are fixed in advance.
- **Controls:** each variant's controls are poured into that variant's own lines and pages:
  - 69 meaningful texts (E099 set);
  - 60 generator stretches (E032 × 10, E100 grid × 50).
- **Bands:** L band = meaningful COMPACT [p10, p90]; G band = generator COMPACT [p10, p90]. A variant is valid iff the
  two bands do not overlap.

| Outcome | Rule | Factor |
|---|---|---|
| GENERATOR-LIKE | Voynich in G band and outside L band in every valid variant (≥ 3 valid) | M × 2 |
| LANGUAGE-LIKE | Voynich in L band and outside G band in every valid variant | M × 1/2 |
| MIXED | anything else | none |
| VOID | fewer than 3 valid variants | none |

- **Rule 8, per variant:** if the Voynich is within 0.5 page-bootstrap sd of a band edge, take 10 bootstraps; at least
  8 must agree, otherwise that variant counts as disagreeing.
- **Unscored:** herbal A (scribe 1) DRIFT and every group's DRIFT, per variant.

## Seen beforehand
- **All of E102,** including the per-group values for V1:
  - Voynich: bathing −0.03, stars +0.04, pharma −0.07, herbal A +0.28.
  - Meaningful medians: +0.14, +0.23, +0.13.
  - Generator medians: +0.01, +0.00, +0.03.
- **Smoke run** (3 texts, 3 generator stretches; no Voynich):
  - V1 L −0.04 to +0.18 vs G +0.06 to +0.13;
  - V2 L +0.23 to +0.33 vs G +0.03 to +0.05;
  - V3 L +0.02 to +0.09 vs G +0.15 to +0.24;
  - V4 L +0.07 to +0.32 vs G +0.11 to +0.22.
- **Not yet seen:** no Voynich value for V2, V3 or V4 has been computed.
