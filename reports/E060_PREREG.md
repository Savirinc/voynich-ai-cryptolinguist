# E060 pre-registration: the ingredient link. Do pharma labels recur in the recipes?

Written 2026-10-25, before the run. Script: `experiments/e060_ingredient_link.py`. Output:
`experiments/results/e060.json`, `e060_run.log`, report `reports/INGREDIENT_LINK.md`. Updates `LEDGER.md`.

## Question
The book is laid out like a fifteenth-century medical compendium: herbal, astrology, bathing, pharmacy (jars and plant
parts with labels), and a long section of about 320 star-marked paragraphs that look like recipes (the "stars"
section, quire 20). **If the labels on the pharma jars and plant parts are ingredient names, they should turn up in
the recipes.** A meaningless text has no reason to reuse its label words in a distant section beyond what their
frequency predicts. This is the "dog that didn't bark" test for the book's own design (`ABSENCE_RULE.md`).

**Terms.** A *label* is a word written beside a drawing rather than in running text. The *recipes* are the prose
tokens of the stars section (illustration code S: f58r–v and quire 20, f103–f116; the locked leaves 105 and 114 are
excluded). *Frequency-matched* means: for every label word, a comparison word that occurs equally often in the whole
DEV text, so that a common label does not get credit just for being common.

## Data (DEV, clean tokens, LOCKED_TEST excluded)
| Set | Definition | Size (design count, seen) |
|---|---|---|
| **Pharma labels** (primary) | label tokens on P pages, ≥ 3 glyphs | 200 tokens, 189 types |
| eligible | DEV total count ≥ 2 (a word seen once cannot be found anywhere else) | **90 types** |
| Pharma text (pool) | non-label tokens on P pages | 1,786 tokens, 774 types |
| **Recipes** (target) | prose tokens on S pages | 9,959 tokens, 21 folios, 245 paragraphs |
| **Herbal first words** (secondary) | first word of line 1 of each Currier-A herbal page | 70 pages, 67 types, 29 eligible |
| Herbal A text (secondary pool) | other prose tokens on those pages | |

The pharma quires (15–19) and the recipe quire (20) are different sheets, so E059's sheet effect cannot produce a
link by itself. They are adjacent in reading order; the neighbourhood effect of E059 (+3 to +4 points) is why the
comparison pool is drawn **from the pharma pages' own text**, which has the same neighbourhood.

## Statistic
- **HIT** = share of eligible label types that occur at least once in the recipes.
- **Null:** 2,000 draws. In each draw every label type is replaced by a random type from the pool with the same
  frequency band (DEV total count: exact for 2–10; bands 11–20, 21–50, 51+; label types themselves excluded from the
  pool; sampled without replacement within a draw where the band allows). The draw's HIT is one null value.
- **p** = (1 + number of null values ≥ HIT) / 2,001, one-sided. **Excess** = HIT − mean(null).
- Reported: the matched label words and how many recipe paragraphs each appears in; the same for the secondary set.

## Controls (both must pass, or the test is VOID)
**Power control (a real compendium).** Culpeper's herbal (`pg_herbal/pg49513.txt`) has plant entries with names as
headings and, after them, a "Directions for making syrups, conserves…" section that uses the plants. Names = the
content words of the all-capitals entry headings between the first entry and the Directions heading (lowercased,
letters only, ≥ 3 letters, stopwords dropped), eligible if they occur ≥ 2 times in the whole text. Target = the first
10,000 words of the Directions section (the Voynich target size). Pool = word types of the entry bodies, not names,
matched on whole-text count with the same bands. To match Voynich's power, **20 random subsamples of 90 names** are
each tested with 500 null draws. **Power** = share of subsamples with p < 0.01. PASS if power ≥ 0.80. The full-set
result is also reported.

**False-positive control (gibberish).** 10 fresh Timm & Schinner generator samples (seeds 21–30, shipped
configuration, 28,841 tokens each; E051 used seeds 11–20). In each: pseudo-pharma region = tokens 20,000–21,785
(1,786 tokens); pseudo-recipes = tokens 10,041–19,999 (9,959 tokens, directly before it, as quire 20 follows the
pharma quires); pseudo-labels = for each real eligible label, one type from the pseudo-pharma region in the same
frequency band (sample-internal counts), 90 in all; pool = the other pseudo-pharma types. Same statistic, 1,000
draws. PASS if **0 of 10** samples reach p < 0.01.

## Decision (primary set only; the secondary set is reported, never scored)
| Outcome | Rule | Ledger |
|---|---|---|
| VOID | a control fails | none |
| **FOUND** | p < 0.01 and excess > 0 | **L × 3, C × 3** (both predict ingredient reuse; M does not). Within L: L-practical share × 10 relative to L-sacred and L-other, then renormalised |
| **NOT FOUND** | p ≥ 0.05 | Absence rule on the searched form "a practical compendium whose jar labels are ingredients reused in the recipes", s = 0.5 of L-practical, m = 0.2: L-practical share × 0.6 within L; **L × 0.82** overall (1 − 0.45 × 0.5 × 0.8); **C × 0.9** (its plaintexts are the same genres; conservative) |
| INCONCLUSIVE | 0.01 ≤ p < 0.05 | seed check: 10 seeds; FOUND only if ≥ 8 of 10 give p < 0.01; otherwise no factor |

Why these factors. Under L-practical (0.45 of L) ingredient reuse is expected; under L-sacred or L-other it is not;
under C it depends on the plaintext genre in the same way; under M (copy-and-change writing, local in reach) a
cross-section link beyond frequency is surprising. The likelihood ratio L : M for FOUND is therefore about 0.5 :
0.1, read on the coarse scale as weak (× 3). The absence factor follows `ABSENCE_RULE.md`.

If the secondary set alone is FOUND, it is recorded as an unscored fact (no model-hunting).

## Seed rule (standing rule 8)
As in the table: a p between 0.01 and 0.05 triggers 10 seeds; a control that passes or fails by one subsample or one
generator sample is re-run with 10 seeds and judged by ≥ 8 of 10.

## What was seen before writing this (disclosed)
- Design counts above (sizes and type counts only).
- E051: labels in own page text 10.5% vs 6.3%. E059: pharma labels in own page text 6.5% vs 5.7%; the echo is a
  neighbourhood effect. E055: same-label pharma drawings do not look alike. The word ledger CSV exists with per-section
  counts; **it was not consulted for any label word**.
- **No hit, null or excess has been computed, for Voynich, Culpeper or the generator.**
- The script's functions will be exercised on fabricated tokens (a planted ingredient link, and none) before locking;
  that check produces no Voynich statistic and is disclosed here.
