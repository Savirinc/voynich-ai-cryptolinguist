# E102 pre-registration: does the vocabulary drift with position, beyond topic? (Arham, Reddit idea R1, 2026-10-31)

## Question
The Reddit claim (1v4hiiz) is that the Voynich's vocabulary changes with position in the book, not with topic. The
copy generator should drift this way, because it copies from recent text. A real book's similarity should follow its
topic.

We ask whether, with topic, scribe, Currier language and sheet held fixed, near pages share more vocabulary than far
pages, and whether the Voynich does this like meaningful texts or like the copy generator.

## Data
- **Voynich pages:** DEV prose pages with ≥ 60 clean tokens, in reading order: 154 pages, 28,841 tokens, LOCKED_TEST
  leaves excluded.
- **Pairs:** two pages with the same Currier language, the same scribe and the same section (illustration), on
  different sheets (C24). Only groups of ≥ 5 pages are used: herbal A scribe 1, herbal B scribe 2, stars B scribe 3,
  bathing B scribe 2, pharma A scribe 1, herbal B scribe 5, herbal B scribe 3.
- **Controls:** each is poured into the Voynich line lengths, so it has the same pages and the same pairs.
  - 69 meaningful texts (E099 set).
  - 60 copy-generator stretches (E032 × 10, E100 grid × 50).
  - Unscored: 5 Naibbe texts, each with one permuted published table, from Italian (ita1885) plaintext.

## Procedure (`experiments/e102_drift.py`)
- **Similarity:** cosine of page word-count vectors, using words that occur ≥ 5 times in the whole text.
- **Drift:** DRIFT = −Spearman ρ(similarity, page-index distance) over the pairs.
- **Bands:** L band = meaningful DRIFT [p10, p90]; G band = generator DRIFT [p10, p90].
- **Validity:** the L and G bands do not overlap.

| Outcome | Rule | Factor |
|---|---|---|
| LANGUAGE-LIKE | Voynich in L band, outside G band | M × 1/3 |
| GENERATOR-LIKE | Voynich in G band, outside L band | M × 3 |
| NEITHER | otherwise | none |
| VOID | bands overlap | none |

- **Rule 8:** if the Voynich is within 0.5 sd of a band edge (sd from 200 page bootstraps), take the first 10
  bootstraps; at least 8 must agree, otherwise NEITHER.
- **Unscored:**
  - DRIFT for each group;
  - the Reddit "late small-plant pages" claim: pharma A scribe-1 pages' mean similarity to herbal A scribe-1 pages,
    compared with their similarity to their 3 nearest pages from other groups.

## Seen beforehand
- **Earlier results:**
  - E054 page topics (VOID);
  - C24 / E059: pages cluster by sheet, which is why same-sheet pairs are excluded;
  - E085: same-plant herbal pages share no words;
  - Reddit's word-rate figures (*ol* 44.4 per 1,000 in bathing vs 11.6 in herbal).
- **Smoke run** (3 texts, 3 generator stretches, 2 Naibbe texts; no Voynich):
  - eng-kjv +0.245, latVUC +0.281, Culpeper +0.268;
  - generator +0.158, +0.229, +0.215;
  - Naibbe +0.189, +0.224, so Naibbe is not flat here.
  - The bands are close, and a VOID is possible.
