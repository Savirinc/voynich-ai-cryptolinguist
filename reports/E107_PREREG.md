# E107 pre-registration: are gallows decorative anywhere in a word, like Arabic kashida? (Arham, 2026-10-31)

## Question
Arham's idea: gallows may be calligraphic decoration anywhere in a word, as the kashida is in Arabic and Urdu writing,
or a scribe's personal style. A decoration does not change the word. So a word written with and without its gallows
(e.g. *kaiin*/*aiin*, *chkol*/*chol*) should be used in the same contexts. If the gallows makes a different word, the
contexts should differ, as they do for real minimal pairs.

## Why not the simpler test
A first draft asked only whether deleting a gallows leaves a real word. On generator text the answer is already 85%
(against 17–20% for other letters), because gallows sit in an optional slot of the word grammar in both the Voynich and
the generator. Planting extra gallows changed nothing (planted OPT +0.68 vs unplanted +0.66 to +0.69), so the draft
could not work. It was dropped before locking and is kept in the scratchpad as `e107_draft_deletion.py`. No Voynich
value was computed with it.

## Data and procedure (`experiments/e107_gallows_context.py`)
- **Pairs:** (w, w′), where w′ is w with one gallows (*t/k/p/f*, also inside the benches *cth/ckh/cph/cfh*) deleted, and
  both occur ≥ 30 times.
- **Context:** the previous and next word within the line, with *#* at line edges. Voynich DEV lines are broken at
  unclean tokens; LOCKED_TEST leaves are excluded.
- **Per-pair CD:**
  - draw 15 occurrences of each word and take the Jensen–Shannon divergence of their contexts (JSD_pair);
  - SAME = the JSD of two disjoint draws of 15 from one word (averaged over w and w′);
  - RAND = the JSD of w against frequency-matched random words (0.7–1.4 × count);
  - 30 draws of each;
  - CD = (JSD_pair − SAME) / (RAND − SAME), so 0 means interchangeable and 1 means as different as unrelated words.
- **Text CD:** the median over pairs.
- **Known answers** (latVUC, ita1885, deu1912, ces1613, turytc, each cut to 28,841 tokens and poured into Voynich
  lines):
  - REAL minimal pairs: a word and itself minus one letter, both ≥ 30 times;
  - PLANTED decoration: a mark inserted at a random interior position of 30% of tokens; pairs are (decorated, plain).
- **Validity:** planted CD maximum < real-pair CD minimum.

| Outcome | Rule |
|---|---|
| DECORATIVE-LIKE | Voynich gallows CD ≤ planted maximum |
| WORD-DISTINGUISHING | Voynich gallows CD ≥ real-pair minimum |
| PARTLY | otherwise |
| VOID | validity fails |

- **No Bayes factor.**
- **Unscored:** Voynich pairs from deleting other letters; generator gallows pairs (10 stretches); results by gallows
  letter.

## Seen beforehand
- E106 (paragraph gallows DECORATIVE, marginal) and E072.
- Davis 2020: scribes are distinguished by the shape of *k* and of final *n*.
- **Smoke run** (no Voynich):
  - real minimal pairs: Latin 0.950 (28 pairs), Italian 0.982 (49);
  - planted decoration: +0.003, −0.010;
  - generator gen0 gallows pairs: 0.718 (15).
