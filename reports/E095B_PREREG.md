# E095b pre-registration (Test B2, Arham): find a key in the zodiac, prove it on the whole book

Written 2026-10-28, before any real crib was scored. Script `experiments/e095b_crib_fullbook.py`; meanings
`reports/data/e095_concepts.json` (locked with E095). Output `experiments/results/e095b.json`, `e095b_run.log`, report
`reports/ZODIAC_CRIB_FULLBOOK.md`.

## Question
E095 was VOID: 12 zodiac pages are too little text to identify a key from meaning matches. Arham: "even if we get one
right, we can test that key properly on all the text". **Does the true crib (each page's own sign meanings) yield a key
that reads the WHOLE book (Voynich A or B prose) better than keys from wrong cribs do?**

## Procedure (per configuration = language × section)
- **Languages with a model on disk:** Latin (Vulgate), French/Occitan list (French Bible LSG as model), Italian, German,
  Hebrew (WLC; meanings converted to Hebrew letters), Arabic (Van Dyck; meanings converted to Arabic letters). Catalan
  and Greek are dropped: no Catalan model on disk, and the Greek model is in Greek script while the lists are romanised.
- **Units:** the VOY23 signs (E047: cleaned EVA, S3 units, the 23 commonest Voynich-A signs; rarer units dropped) for
  both the zodiac words and the book. **Sections:** Voynich A prose (8,794 words) and B prose (19,488 words).
- **Stage 1 (zodiac).**
  - Meaning targets of >= 4 letters (in the model's letters); matches are exact or abbreviation >= 6, forwards or
    backwards (as E095).
  - Search: greedy consistent key construction, 2,000 restarts. On each page one of the 3 candidates that make the book
    most plausible is chosen at random; plausibility = mean model letter-bigram log-probability over the book's bigrams
    whose two units the key fixes.
  - Keys covering >= best − 1 pages are ranked by plausibility; the top 8 go on.
- **Stage 2 (whole book).** Each key is completed by the E047 annealer with its units held fixed (2 restarts × 8,000
  steps) under the language's 4-gram model; score = best objective per sign. The crib's score is its best key's score.
- **Null:** 99 wrong cribs (meaning sets shuffled among the 10 signs, two-page signs together), each run through the
  same stages. Per configuration z and p; **max-T over the 12 configurations** (each standardised by its own null).
- **Calibration (run in the same job, must pass first):** synthetic books (E047 VOY23 cipher of held-out Bible text,
  Voynich-A length) with synthetic zodiac pages of the real word counts from the same cipher, each holding one planted
  own-sign meaning word; Latin, French, Hebrew. Each must give p <= 0.01 (true crib above all 99 wrong cribs), else VOID.

## Decision
| Outcome | Rule | Ledger |
|---|---|---|
| VOID | any calibration p > 0.01 | none |
| **CLAIM** | p(max-T) <= 0.01 | none yet: seed check of the best configuration (10 fresh runs, >= 8 at p <= 0.01), then the decoded text is shown to Arham and to blind readers; only a confirmed reading moves the ledger |
| NO CLAIM | otherwise | none (narrow form; recorded with the zodiac campaign) |

## Disclosed
- E095 results (VOID; unscored Voynich max-T p 0.16).
- **Development on synthetic known answers only (no real crib scored).** Smoke runs with 4 wrong cribs:
  - First version: Hebrew calibration failed. Diagnosis: the true crib key was never generated, not a weak completion
    (unconstrained completion reaches the true score).
  - Stage 1 was changed twice (bigram plausibility ranking; plausibility-guided choice; restarts 300 → 2,000).
  - Final smoke: Latin z +2.2, French +5.3, Hebrew +7.9.
- One known limitation: a single key for a whole section is assumed (A and B are tested separately).
