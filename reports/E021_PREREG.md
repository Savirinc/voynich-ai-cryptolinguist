# E021 pre-registration: methodology test A1c — do the most common Voynich words persist across the book?

Written 2026-10-18, BEFORE the full run. A smoke run (1 twin sample per family/language; Voynich NOT computed)
showed the expected contrast is moderate, not total: PERS_30 word 0.41, compound 0.42, naibbe_drift4/8 0.28/0.21,
word_drift4 0.12, fixed-key naibbe 0.71, rugg 0.72, self-citation 0.16. A changing-key Naibbe cipher keeps its
frequent glyph strings frequent, because every key reuses the same inventory. No setting was changed after it.

## Question
In language, grammar words occur everywhere; under changing keys or tables, the frequent types are reshuffled.
Where does Voynich fall?

## Statistic (experiments/e021_persistence.py)
8 equal chunks in reading order; for the top-T types (T = 30, 100): ratio = chunk rate / overall rate.
PERS_T = mean of the minimum ratio; COV_T = mean share of chunks with ratio >= 0.25.

## Families (unchanged generators from E019 and E020; seed 21021)
word, syll, naibbe (fixed key), naibbe_drift4, naibbe_drift8, word_drift4, compound, compound_drift4: 40 samples
each (10 x la/it/fr/de); rugg_rep, self_citation_rep: 20 each. At DEV size (primary) and Currier B size (secondary).

## Decision rule (fixed now)
CONSISTENT iff |z| <= 3 on PERS_30 and COV_30 (z vs the family's samples). T = 100 reported, not used.

## Interpretation fixed now
- naibbe_drift4 and naibbe_drift8 both inconsistent, word or compound consistent → the frequent Voynich types
  behave like grammar words; the changing-key cipher loses its remaining support from A1/A1b.
- naibbe_drift consistent → A1c cannot separate the two; A2 (labels against pictures) and B1 must decide.
- Combined with E019/E020: the families consistent here AND closest in E020 are carried into Stage B.

## What this cannot show
Moderate expected contrast. The equal chunks do not follow Voynich's real section or scribe boundaries.
