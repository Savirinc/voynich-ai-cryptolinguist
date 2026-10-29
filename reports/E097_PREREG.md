# E097 pre-registration (Arham): one key for the whole book, letters borrowed from several period scripts, zodiac anchor

Written 2026-10-29, before the method touched the Voynich text. Script `experiments/e097_one_key.py`; new period texts in
`data/external/period_texts_e097/` (Wikisource: Ramon Muntaner's Catalan chronicle, 301 chapters; Old Occitan
troubadour poems and the Béziers *Libre de Memorias*). Output `experiments/results/e097.json`, `e097_run.log`, report
`reports/ONE_KEY_MANY_SCRIPTS.md`.

## Question (Arham's design)
- One key for the whole book. The common words run through all five scribes and both A and B, so several keys are
  ruled out by design.
- The writer may have borrowed letters or features from several scripts in use around 1404–1438 in the region.
- The zodiac pages are taken as meaningful (the anchor).

**Is there one key, mapping each Voynich sign to one sound or one scribal shorthand, under which:**
1. the half of the book the key never saw reads as words of period languages; and
2. the zodiac pages it never saw contain words naming their own sign's month, sign, animal, planet, element, season
   or fixed stars?

## Model
- **Ten languages** (Arham's table), each rewritten in **one 30-sound alphabet** with period pronunciation rules:
  Latin, Italian, Occitan, Catalan, French, German, Czech, Greek, Hebrew, Arabic.
  - Texts:
    - Bibles on disk (Vulgate; Italian 1885; French LSG; German 1912; Czech Kralice 1613; Byzantine Greek NT; Hebrew
      WLC; Arabic Van Dyck);
    - Muntaner (Catalan, 14th century);
    - Old Occitan (troubadours and *Libre de Memorias*).
  - Each corpus is split: one part trains the language model, a separate part feeds the known answers.
  - Glagolitic/Cyrillic use is represented only by Czech, since no Church Slavonic text is on disk.
  - Judeo-Italian and Shuadit are not available.
  - French and German are modern Bible spellings; Occitan is small (about 24,000 words for its model).
- **Key:** each of the 23 VOY23 signs maps to one sound or to one of 10 shorthand values (us, um, is, er, ur, rum,
  con, per, pro, que). The key is the same for the whole book. **Each line may be in any of the ten languages.**
- **Objective:** sum over lines of the best language's 4-gram Kneser-Ney log-probability, minus the per-language
  letter-frequency penalty (E047).
- **Split:**
  - Zodiac pages alternate: training f70v2, f71r, f72r1, f72r3, f72v2, f73r; held out f70v1, f71v, f72r2, f72v3,
    f72v1, f73v.
  - All other pages are split by **sheet** (bifolio; C24), half and half by seed.
  - LOCKED_TEST leaves are excluded.

## Procedure (identical for every book, real or synthetic)
1. **Anchor (stage 1).** On the 6 training zodiac pages, partial keys are built under which page words (3 or more
   signs) read exactly as own-sign material (sound strings of 3 or more). The material comes from the E095 lists in 8
   languages plus Lilly's fixed-star names. Search: greedy consistent construction (2,000 restarts); the top 8 keys by
   plausibility go on.
2. **Whole book (stage 2).** On the training half of the book: one free start plus the 8 anchor keys (anchor signs held
   fixed), each annealed for 20,000 steps.
3. **Refit.** This is the mixed-language trap breaker, added after development on synthetic books. For the 2 best
   starts, 3 rounds are run. In each round, the worse-read half of the lines is re-fitted from scratch under each single
   language in turn (8,000 steps), then the whole key is re-annealed on all lines with all languages (8,000 steps). A
   candidate is kept only if the objective rises. The best result is the fitted key.
4. **Held-out checks.**
   - **Q1:** the share of distinct decoded word types (3 or more sounds) found in the vocabulary of their line's
     language.
   - **Q2:** on the 6 held-out zodiac pages, count the pages with a **new** word (not on any training zodiac page)
     that reads as its own sign's material. Compare against all 720 assignments of the six signs to the six pages;
     p is the share of assignments scoring at least as high.

## Known answers and controls (same job, run first)
- **Synthetic books:**
  - Built with the exact Voynich line structure, from held-out period text in 20-line language blocks.
  - Cipher: a random key with 2 shorthand signs (for the plaintext's two commonest clusters, used 70% of the time)
    and at least one sign per kept sound; spare signs are homophones; 12% spelling slips.
  - Each of the 12 zodiac pages gets one planted own-sign word.
- **DEV (sets the Q1 threshold):** D1 Latin; D2 Catalan+Latin; controls DC1 generator (Timm & Schinner) and DC2
  Voynich with its signs shuffled. Threshold = midpoint between the lowest cracked known answer and the highest
  control; the known answers must lie above every control, else NOT VALIDATED.
- **TEST:**
  - known answers T1 Italian+Hebrew, T2 Czech+German+Latin, T3 Greek+Arabic+Latin, T4 Occitan+Catalan;
  - controls TC1 generator, TC2 Voynich shuffled, TC3 T1 shuffled, and TC4 generator with planted own-sign words on
    the **training** zodiac pages only (an anchor without meaning).
- **CLAIM rule (any book):** Q1 ≥ threshold **and** Q2 p ≤ 0.05.
- **VALID** if:
  - DEV separates;
  - at least 3 of the 4 TEST known answers are claimed with key accuracy ≥ 0.80 (held-out sign tokens decoded to the
    true value);
  - no control is claimed, and no claim is made with accuracy < 0.80.

## Decision
| Outcome | Rule | Ledger |
|---|---|---|
| VOID | not VALID | none; the Voynich result is shown unscored |
| **CLAIM** | VALID and Voynich claimed | none yet: rule-8 seed check (10 fresh seeds, ≥ 8 claimed); then the decoded held-out pages are shown to Arham with English, then readers; only a confirmed reading moves the ledger |
| NO CLAIM | VALID and Voynich not claimed | the searched sub-form (one key, period languages of the region mixed by line, shorthand values) within L-alpha-known: share × 0.8 (not the absence rule's 0.2: E090 showed the vocabulary gate weakens out of genre). L × 0.943 |

Whatever the outcome, the fitted Voynich key and decoded passages (Voynich, decoded text, English) are shown to Arham
as exploration.

## Seen beforehand (disclosed)
- E047–E089 attack results; E095, E095b, X096, E096, X098; the X098 Arabic Key 1 f70v1 readout shown to Arham.
- **Development on synthetic books only; this engine has not been run on Voynich text.**
  - First version: Latin and Catalan+Latin cracked (accuracy 0.99–1.00, held-out zodiac 6/6); shuffled Voynich token
    lexrate 0.07, generator 0.29.
  - Normalising line scores by each language's typical entropy made Greek+Arabic+Latin worse, so it was dropped.
  - Token lexrate let the generator reach 0.24–0.29, so Q1 was switched to word types (cracked 0.45–0.54; generator
    0.08–0.10; shuffled 0.05; trapped mixture 0.16).
  - Italian+Hebrew was stuck at accuracy 0.70. Diagnosis: a search trap, not a model failure (true key objective
    −202k vs found −273k; each language half alone cracks at 0.99). The refit step reached 0.988.
  - With refit, Czech+German+Latin reached 1.00 and Occitan+Catalan 0.995.
