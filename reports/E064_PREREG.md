# E064 pre-registration: re-audit of the early ledger factors (E030–E032), and the E051 re-measurement forced by a tokenizer defect

Written 2026-10-25, before the run. Script: `experiments/e064_early_audit.py`. Output: `experiments/results/e064.json`,
`e064_run.log`, report `reports/EARLY_AUDIT.md`. Updates `LEDGER.md`.

## Why
L's lead was built in three steps on 2026-10-21: E030 (L × 3: languages that double words reach Voynich's repeat rate),
E031 (L × 3: one text, a Czech spelling primer, shows both exact copies and near-copies above chance) and E032 (M × 1/3:
the Timm & Schinner generator fails 7 of 13 features). Since then: E059/E062 showed that the book's heterogeneity (five
scribes, sheets) by itself fixes the persistence, coverage and Zipf-head failures for a cipher twin; E051 reported that
fresh languages (Tamil, Assamese) reach Voynich's back-to-back repeat level; E058 found Voynich's words repeat the way
their families predict, like the generator. CLAUDE.md step 2 asks for a pre-registered audit of these factors, not hand
edits. Each part below can move the ledger by at least × 3 (gate met).

## Tokenizer defect found while preparing this (disclosed before the run)
Both Bible loaders used so far (`e030.tokens`, `e042.words`) define a word as a run of `\w` characters. Combining marks
are not `\w`, so scripts whose vowels are written as marks (Tamil, Malayalam, Assamese/Bengali, Gurmukhi, Devanagari)
were cut into single-letter fragments: Tamil 1,724,888 "words" instead of 432,604 real ones, `['ர', 'த', 'வன', 'அத']`.
Latin-script texts are affected only at apostrophes and rare uncomposed tone marks (0–12% of tokens).
**Affected results:** E051 Part 1 (its two "matches", Tamil 1.01 and Assamese 0.87, and the next five highest AS values
are exactly the seven fragmented languages); E057/E058 (Tamil, Assamese, Malayalam references "not computable");
E061 (Tamil's 1,046 word types widened the language spread that made the rule uncalibrated); E063 (seven of the 49
languages were attacked as fragment streams: validated and no claim, but not a test of the real language);
E031's PG Telugu row. E030's primary languages are Latin-script and unaffected.
**Fix:** TOK = maximal runs of letters (Unicode L*), marks (M*) and apostrophes, on lowercase NFC text. Part C below
re-measures E051 with it. Earlier numbers are not edited; the ledger records the correction.

## Part A: E031 on fresh data (does any ordinary language do both?)
- **Data:** the 30 E051 languages (`e051_ids.txt`), none seen by E031; TOK words; 10 windows of 28,841 tokens per
  text, seed 64064 + index.
- **Statistics:** E031's R (exact neighbour copies ÷ Σp²) and NR (near-copies ÷ shuffled, 5 shuffles).
- **Rule (E031's):** a text does both iff R ≥ 1.5 and NR ≥ max(1.5, 0.67 × Voynich NR), Voynich NR recomputed on DEV.
- **Seed rule:** a text within 0.1 of either bar is re-measured with 10 fresh window draws; ≥ 8 of 10 decide.

| Outcome | Rule | Ledger |
|---|---|---|
| E031 CONFIRMED | ≥ 1 of 30 does both | none; the fragility note ("rests on one drill text") is closed |
| E031 WITHDRAWN | 0 of 30 does both | **L × 1/3** (E031's factor removed; "does both" remains a drill-text property, 1 of 183 texts) |

Also reported: which of the 30 reach R ≥ 1.5 (a free replication of E030, whose factor stands either way: E030's
finding was that a language *can* do it, and Indonesian/Malay are unaffected by the defect).

## Part B: E032 with five scribes (was the generator's failure a failure of homogeneity?)
- **Construction (mirrors E062, no tuning):** the Timm & Schinner generator with the authors' shipped settings, one
  run per scribe (seed 100·sample + hand), consumed line by line along the DEV hand runs in manuscript order (33 runs;
  tokens per hand 8,061 / 8,838 / 10,534 / 539 / 869; '@' lines to hand 3). Generator lines are kept, truncated only
  at run boundaries. 10 samples of 28,841 tokens.
- **Battery and rule (E032's):** 13 features, |z| > 3 fails (sd floor 2% of the Voynich value).
- **Seed rule:** a feature within 0.5 of |z| = 3 is re-judged on samples 11–20 with 10 bootstrap draws of 10 samples
  from the 20 (≥ 8 of 10 agree); an undecided feature forces PARTIAL if the verdict depends on it.

| Outcome | Rule | Ledger |
|---|---|---|
| M REPRODUCES | ≤ 1 fail | **M × 9**: E032's × 1/3 is withdrawn (× 3) and × 3 is applied for an untuned reproduction (E062's weak factor for a static battery, mirrored) |
| PARTIAL | 2–4 fails | **M × 3**: E032's × 1/3 is withdrawn (E032's own table gives no factor for PARTIAL); the surviving failures are recorded as what M still lacks |
| FIVE-SCRIBE GENERATOR FAILS | ≥ 5 fails | none; E032 stands |

Why the retrospective logic: E032 asked whether the authors' generator reproduces Voynich's facts, and its own report
named homogeneity as a possible cause of the persistence failure. Voynich has five scribes (C). Giving the generator
that structure is the same courtesy E062 gave the cipher, and the result is read through E032's own table.

## Part C: E051 Part 1 re-measured with the fixed tokenizer
- Same 30 languages, same window (words 2,000–30,841), same exclusion (mean token length > 15), same pseudo-lines
  (Voynich DEV line lengths), same statistic AS = ΣO ÷ ΣE and threshold 0.85, same generator values (seeds 11–20,
  unaffected by the defect, taken from `e051.json`).
- **Rule (E051's):** k_L = fresh languages with AS ≥ 0.85; p_L = (k_L + 0.5)/(n_L + 1), p_M = (k_M + 0.5)/(n_M + 1),
  BF(M:L) = p_M/p_L; factor on M by E051's bands (≥ 10 → × 10; 3–10 → × 3; 1/3–3 → none; 1/10–1/3 → × 1/3; ≤ 1/10 →
  × 1/10). The result replaces E051's Part 1 entry.
- **The E045 caution** ("C21 leans towards M") is **reinstated** iff k_L = 0; otherwise it stays withdrawn.
- Arithmetic in advance: with k_L = 0, p_L = 0.016, p_M = 0.045, BF 2.8 → no factor (band 1/3–3). With k_L ≥ 1, BF ≤ 1.
  So Part C can move the ledger only if k_L = 0 **and** the band changed, which it does not; its effect is on the
  caution and the record.

## Ledger after E064
Factors from A, B and C multiply onto M 0.0083, L 0.9808, C 0.0095, O 0.0014, then renormalise. Sensitivity from the
range edges is reported. One attempt for each part (standing rule 9).

## Disclosed
- E030–E032's results and factors; E051's values (Tamil 1.01, Assamese 0.87, Malayalam 0.76, generator max 0.81);
  E062's finding that per-scribe heterogeneity fixes persistence, coverage and the Zipf head for a cipher.
- Token counts and mean token lengths of the 30 languages under both tokenizers (above); the DEV hand run structure.
- Not computed on any of the 30 languages with TOK: R, NR, AS. No five-scribe generator sample has been generated or
  measured. The construction was exercised on fabricated text (a toy hand sequence and fake streams) and the dry run
  only loads data and counts tokens.
