# Results as plain test outcomes, and how much the Bayes ledger depends on judgement (publication step 2)

The paper reports results in this order:
1. **Plain outcomes** (Table A). Each was a locked rule decided before the run, so no Bayes factor is needed to read it.
2. **The two patterns** they show.
3. **The Bayes ledger, as an illustration only** (Table B), with a sensitivity analysis (Table C).

## Table A: decisive tests between meaning and a meaningless process (VALID tests only)
"Language range" and "generator range" are the known-answer bands each test was validated on.

| Test | Question | Voynich | Language range | Meaningless range | Outcome |
|---|---|---|---|---|---|
| E066 | Do common words repeat individually or by shape family? | z −1.2 | +4 to +14 (4 separating languages) | generator ≈ 0 | **meaningless side** |
| E067 | Distinct words per 150 tokens | 112 (62% once-only) | Bibles 95 (47%) | human gibberish 115 (67%); copy generator 94 | **human-gibberish side** |
| E085 | Do pages of the same plant share words? | p 0.61 | Culpeper p 0.0001 | — | **no link** |
| E100 | Phrase reuse (Q3), richness-matched | 10.8 | ≥ 13.6 | ≤ 6.5 | **between** |
| E100 | Repeated 4-word phrases | 0 | ≥ 223 | 0–11 | **meaningless side** |
| E104 | Word-pair order preference (ASYM) | 0.18 | ≥ 0.43 (Latin verse 0.56) | 0.12–0.18 | **meaningless side** |
| E116 | Phrase reuse after merging the 5 spelling families | 2.41 | ≥ 5.01 | ≤ 3.84 | **meaningless side** |
| E119 | Are label words introduced at paragraph openings, as names are? | −0.033 | Culpeper +0.054 | ≤ +0.028 | **meaningless side** |
| E069 | Common-word partners persist across halves | 0.073 | p10 0.083 | ≤ 0.053 | between |
| E070 | Content-word partners persist | 0.004 | ≥ 0.018 | generator median | below all languages (rule safeguard failed by a hair) |
| E093 | Same-subject pages share vocabulary | z +1.2 | +14, +16 | −2.4, −5.0 | inconclusive |

**Does a specific meaningless process reproduce the Voynich?**

| Test | Process | Result |
|---|---|---|
| E032 / E064 | Timm & Schinner copy generator (published code), 1 and 5 scribes | fails 7/13 features |
| E068 | 36 humans writing gibberish | Voynich-like on 1 of 5 features |
| E093 | Process ladder P1–P4 | 5/12 facts |
| E114 | Dice word tables (252 settings) | best fails 7/13 |
| E120 | "Habit writer" (after quimqu 2026, Parisel 2026), tuned on 13 features | 5/13 fails; 5/10 held-out facts |

**Does a known language hide behind a letter cipher?** Validated attacks on about 60 languages, on Currier A and B,
found no claim in any language (E049–E063, E080–E089, E097). E118 shows the attack recovers keys from 125 words, so
these absences are informative. Whole-word codes cannot be attacked statistically at this length (E118).

## The two patterns
1. **The Voynich is never on the language side.** Of the 11 VALID tests between meaning and meaninglessness in
   Table A:
   - six put it on the meaningless side;
   - two between;
   - one with no link where a herbal links;
   - one below every language;
   - one inconclusive;
   - **none on the language side.**
2. **No meaningless process reproduces it.** Every specific process tested fails a third to a half of the facts. The
   facts they miss are:
   - some short-phrase reuse;
   - richer vocabulary;
   - sheet-level sharing;
   - page-opening surprise;
   - long-range letter links.

**Honest summary:** the text lacks every signature of language we can measure, and nobody, including us, can yet
make it.

## Table B: the Bayes ledger (illustration)
- **Starting point:** the audited ledger of E091 (M 0.463, L 0.360, C 0.098, O 0.079).
- **Factors applied after it, all fixed before each test:**
  - E097 L × 0.943;
  - E098 C × 0.653;
  - E104 M × 3;
  - E114 M × 0.9;
  - E116 M × 3;
  - E119 M × 1.5;
  - E120 M × 0.9.
- **Result:** M 0.913, L 0.061, C 0.012, O 0.014.
- **Caveat:** the factor sizes are judgements, not measurements.

## Table C: sensitivity (`tools/ledger_sensitivity.py`)
| Variant | M | L | C | O |
|---|---|---|---|---|
| As pre-registered | 0.913 | 0.061 | 0.012 | 0.014 |
| Every factor halved in strength (f^0.5) | 0.751 | 0.172 | 0.039 | 0.039 |
| Every × 3 replaced by × 1.4 (the ratio E091 measured for E066) | 0.696 | 0.214 | 0.040 | 0.050 |
| Without E104 | 0.778 | 0.157 | 0.029 | 0.036 |
| Without E116 | 0.778 | 0.157 | 0.029 | 0.036 |
| Without both E104 and E116 | 0.538 | 0.325 | 0.061 | 0.075 |
| Start at E091's M-favoured edge | 0.955 | 0.024 | 0.009 | 0.012 |
| Start at E091's L-favoured edge | 0.838 | 0.128 | 0.017 | 0.018 |
| L-favoured edge, factors halved | 0.599 | 0.311 | 0.049 | 0.042 |

**Reading:**
- **M leads in every variant**, between 0.54 and 0.96.
- **The size of the lead rests mainly on two word-order tests** (E104 pairs, E116 phrases). They are related: both
  measure fixed word order. Without them, M 0.54 vs L 0.33.
- The paper therefore states: "every variant favours a meaningless process; the strength of that preference depends
  on how much weight two related word-order tests are given".
