# E084 pre-registration: mixed-language sources (Hebrew with its associates and with other languages)

Written 2026-10-27, before the run, at Arham's direction ("what if the language is a cipher of two multiple languages
or a real language inspired by two different languages - why we assume it has to be just one?"). Script
`experiments/e084_mixed_sources.py` (imports the locked E083 construction unchanged); output
`experiments/results/e084.json`, `e084_run.log`; report section in `reports/HEBREW_CAMPAIGN.md`.

## Sources
- Real mixed text: **Talmud Bavli** (Berakhot, Shabbat, Pesachim to 200,054 words; Sefaria, William Davidson vocalised
  edition, marks removed), Hebrew and Aramaic mixed as written.
- Mixtures made by alternating 10-word stretches: Hebrew + Aramaic (Onkelos), Hebrew + Judeo-Arabic (Saadia), Hebrew +
  Latin, Hebrew + Turkish, Hebrew + Greek (Hebrew-containing set); Latin + German, Turkish + Greek, Latin + Greek
  (comparison set); letter-scrambled Hebrew + letter-scrambled Latin (meaningless).
- For the letter attack, mixtures in one alphabet: Talmud, Hebrew + Aramaic, Hebrew + Judeo-Arabic (Hebrew letters);
  Hebrew transliterated (E062 table) + Latin, + Turkish; Latin + German, Latin + Turkish (comparisons).

## Part 1: the E083 construction on every mixture
Exactly E083 (data-driven affix lists, 60,000 steps, 3 restarts, order test with 200 shuffles).
- **Known answer:** a second Talmud window (tokens 60,000–88,840) under a hidden random table; fitting from the first
  window must decode ≥ 50% of tokens to the exact word with order z > 3, else VOID.
- **Specificity:** the best Hebrew-containing fit must exceed the best comparison fit by > 0.05.
- **Order:** the best Hebrew-containing order z must be > 3 **and** above every comparison and meaningless mixture's z
  (E083 showed that Voynich's own habits give positive z for any source).
| Outcome | Rule |
|---|---|
| CONSTRUCTION HOLDS | valid, specificity and order both pass → blind reading and LOCKED_TEST prediction next |
| one check only / neither | recorded; no factor |

## Part 2: the E063 letter attack with mixture language models
Model from the first 60% of each stream, plaintext from the rest; 2 cracks, 2 generator + 5 pseudo-A controls,
Voynich A, 5 pseudo-B controls, Voynich B; E063 VALIDATED and CLAIM rules. A CLAIM leads to a blind reading and a
LOCKED_TEST prediction; NO CLAIM, validated, records the mixture as excluded within H1's scope.

## Disclosed
E080–E083 (in E083, Aramaic gave the highest order z, +8.0; Turkish fitted best). Stream sizes printed above the run.
No mixture has been fitted to Voynich or attacked. One attempt.
