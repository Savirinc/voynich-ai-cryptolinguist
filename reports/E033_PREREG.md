# E033 pre-registration (ledger test 4): real languages through the same features as E032

Written 2026-10-21, before the run. Script: `experiments/e033_language_features.py`. Updates `reports/LEDGER.md`.

## Question
E032 tested the meaningless hypothesis (M) by putting the authors' generator through 13 Voynich features. L's rise in
the ledger so far came from removing objections, not from a match. The counterpart: **does any real-language text
match Voynich on the same features?**

## Which features, and why only 8 of the 13
L says Voynich is a language written in its *own* script. Features that depend on spelling would compare our Latin
alphabet with Voynich's glyphs, not language with language:
- h2 and word length (wl_mean);
- near-copies (NR), since "one letter different" depends on the letters;
- the ending inventory (NSUF95, DIST).

Those 5 are dropped. The remaining **8 features do not change under any one-to-one spelling of words**, so they are
fair to L:
- R (exact copies of neighbouring words ÷ chance);
- types;
- I_word and top_word (topic clustering);
- PERS_30 and COV_30 (persistence);
- type_hapax and zipf_slope (vocabulary spectrum).

For comparison, E032's generator on the same 8 features:
- passed R and I_word;
- failed the other 6.

## Data
- **Texts:** the 12 E030 Bibles whose tokens are words, which are the 10 primary texts plus the Latin and English
  anchors: Indonesian, Malay (New Testament), Tagalog, Cebuano, Swahili, Yoruba, Hausa, Hawaiian, Tongan, Māori,
  Latin, English. The syllable-token texts (Vietnamese, Mandarin) are left out, as in E030/E031.
- **Samples:** for each text, 10 non-overlapping consecutive windows of 28,841 tokens chosen at random (seed
  33033), or all of them if there are fewer (minimum 3; Malay NT gives 5).
- **Voynich:** DEV, the same values as E032.
- **Not included:** the Czech primer (E031) and the PG and Latin Library files. They are too short for 3
  independent windows.

## Decision (same z rule and sd floor as E032)
- For each text, z = (Voynich − text mean) ÷ sd, where the sd is the larger of: the sd over windows, 2% of
  |Voynich|, and 0.01.
- A feature fails if |z| > 3. The best text is the one with the fewest fails, with ties broken by RMS z.

| Outcome | Rule | Bayes factor |
|---|---|---|
| A LANGUAGE MATCHES | best text fails at most 1 of 8 | L × 3 |
| PARTIAL | best text fails 2 | none |
| NO LANGUAGE MATCHES | best text fails 3 or more | L × 1/3 |

**Why the factors are symmetric (×3 each way), not like E032.**
- L gets 12 tries against M's one generator, which makes a match easier.
- A failure is weak evidence, just as it was for M: our sample is 12 Bibles, and Voynich is not a Bible.

## What was seen before writing this (disclosed)
- Voynich's values on these 8 features (E032).
- Fragments from earlier tests, at slightly different settings:
  - E028 pooled BIBLE_EU (Latin and English Bibles) gave I_word 0.452 and PERS_30 0.360;
  - E030/E031 gave R for all 12 Bibles.
- No other feature has been computed for these Bibles.

## Limits
- Bibles are translations on one subject matter, while Voynich DEV mixes herbal, astronomical, biological and
  recipe sections. Persistence and topic features may therefore favour or disfavour Bibles for reasons of genre,
  not language.
