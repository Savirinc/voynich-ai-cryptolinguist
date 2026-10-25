# E066 pre-registration (E058 v3): word-specific self-repetition, with correct words and every language on disk

Written 2026-10-25, before the run. Script: `experiments/e066_word_individuality_v3.py`. Output:
`experiments/results/e066.json`, `e066_run.log`, report `reports/WORD_INDIVIDUALITY_V3.md`. Updates `LEDGER.md`.

## Why a v3 is allowed
E058's pre-registration said "no v3 unless a new fact calls for it". The new fact is the tokenizer defect (E064): three
of E058's five reference languages (Tamil, Assamese, Malayalam) were single-letter fragments, so its VOID ("only
Indonesian separates from the generator") was a verdict on broken references. This is the one reopening of the family.

## Question (unchanged)
Do individual words differ in how often they stand right next to themselves, beyond what their **family** (same first
unit, same last two characters) predicts? A real vocabulary gives words individual behaviour: in Indonesian some words
double freely and others never. A copy-and-change process works on word *shapes*, so every word repeats about as its
family does.

**Terms.** *Back-to-back repeat*: the same word twice in a row within a line. *Expected* E_w: how many such repeats word
w would have if the words of each line were in random order (exact within-line formula). *Family rate*: one repeat
rate shared by all words of a family. The statistic G measures how badly one rate per family fits the observed counts;
z and p come from re-drawing the counts under the family model 2,000 times.

## What changes from E058
1. **Reference languages:** every Bible on disk (60; cmn-cu89s, jpn1965 and vie1934 syllable-spaced, lit too small,
   engWycliffe partial are excluded), tokenized with E064's TOK (letters, marks, apostrophes), words 2,000–30,841 in
   Voynich-length pseudo-lines.
2. **Power gate, set on inputs not outcomes:** a language is MEASURABLE iff it has ≥ 20 kept words (count ≥ 10, in
   families of ≥ 2) and total expected repeats E ≥ 30. E depends only on word counts and line lengths.
3. **Generator:** 20 stretches of the E032 output (10 decide; 10 in reserve for the seed rule).
Statistic, eligibility (count ≥ 10), family definition and watched words are E058's.

## Decision (E058's, with the gate)
| Outcome | Rule | Factor |
|---|---|---|
| VOID | fewer than 3 measurable languages have z above every one of the 10 generator stretches **and** p < 0.01 | none; Voynich's own verdict is reported unscored |
| **WORD-SPECIFIC** (vocabulary-like) | Voynich z > every generator stretch and p < 0.01 | **M × 1/3** |
| **FAMILY-LEVEL** (generator-like) | Voynich z ≤ the generator median | **M × 3** |
| INCONCLUSIVE | otherwise | none |

**Seed rule:** if Voynich's z is within 0.5 of the generator maximum or median, the verdict is re-judged on 10 random
draws of 10 stretches from all 20; ≥ 8 of 10 must agree, else INCONCLUSIVE.

**Why the factors are weak (× 3).** M is represented by one generator family; L by Bibles. A word-specific Voynich would
be the first sign that individual words carry identity, but it could also come from a scribal habit keyed to particular
words. A family-level Voynich matches the generator but also matches a language whose doubling is purely phonological.

## Disclosed
- E057/E058's numbers: Voynich z +0.4 (26 words) and −1.1 (112 words, O 188 / E 189); Indonesian +5.1 and +4.8; Malay
  +1.3; generator −1.7 to +2.6. Voynich's watched words (aiin 0/6.5, daiin 11/21.8, qokeedy 16/9.1, dal 1/2.9, shey
  1/3.6). These Voynich and generator values will be recomputed with new seeds and are expected to be similar.
- E064's AS values for the 30 E051 languages (Assamese 0.75 highest); E030's R values (Indonesian 3.03, Malay 1.71).
- No E066 statistic has been computed for any language with TOK. The code was smoke-tested on fabricated lines only.
- Sixty languages will run whatever their AS; which of them are measurable is unknown.
