# E063 pre-registration (campaign step 3): the validated letter attack on every remaining language on disk

Written 2026-10-25, before the run. Script: `experiments/e063_wide_attack.py`. Output: `experiments/results/e063.json`,
`e063_run.log`, report `reports/WIDE_ATTACK.md`. Updates `LEDGER.md`.

## Question
E047 validated an attack on the VOY23 class (a real language written letter by letter in the 23 commonest Voynich-A
signs, with homophones and 12% spelling slips, word boundaries kept). E049, E052 and E053 ran it for 10 languages and
abbreviated Latin: no claim. Fifty more languages sit on disk unsearched. **Does the same validated attack find any of
them in Voynich A or B?** This is the "throw compute at it, judge strictly" step: breadth, with the known-answer
validation and zero-false-claim rule unchanged.

## Languages (50)
Every Bible translation under `data/external/bibles/` not yet searched, except four: cmn-cu89s and jpn1965 (far too
little text), lit (too little text), vie1934 (syllable-spaced; that is the L-syll form, not this class).
Already searched and excluded here: hboWLC, turytc, latVUC, ces1613, srp1865, hrv, slk, ukr1871, ron1924, ita1885, rmc.
Among the 50: German, Dutch, Danish, Swedish, English (two), French, Polish, Greek, Hungarian, Yiddish, Arabic, Urdu,
Uyghur, Persian-script and Indic (Panjabi, Hindi-type, Assamese, Malayalam, Tamil), Indonesian, Malay, Tagalog,
Cebuano, Ilocano, Hiligaynon, Swahili, Yoruba, Hausa, Ewe, Lingala, Luo, Kikuyu, Nyanja, Shona, Hawaiian, Tongan,
Māori, Yapese, and others. Scripts other than Latin are handled as in E052: diacritics and combining marks removed,
the 23 commonest letters kept; the test is crude for abugidas and is declared as such.

## Procedure (exactly E052, with Currier B added)
Per language, with the language model built from books disjoint from the plaintext books (Old Testament books if the
translation has Genesis, else the gospels and Acts; plaintext from the complementary set):
1. **Validation:** 2 VOY23 ciphers of the language's own text (fresh keys, E047 encoder, Voynich-A sign weights) are
   attacked. Each must be cracked (letter accuracy ≥ 0.80, agreement ≥ 0.95). 7 controls with the same model: 2
   copy-generator streams and 5 pseudo-Voynich-A texts (E050's order-2 Markov imitation). VALIDATED iff both cracks
   succeed and the lowest crack lexrate exceeds the highest control lexrate; T = their midpoint.
2. **Voynich A** (DEV, clean, S3 units, 23 signs): CLAIM iff VALIDATED, agreement ≥ 0.95, lexrate ≥ T and lexrate >
   max control + 0.05.
3. **Voynich B** (same signs and model): 5 pseudo-Voynich-B controls of its own; CLAIM rule as for A, with T from the
   same cracks and the B controls' maximum. B is secondary: its sign inventory differs from A's (E041), so a miss on B
   is weaker evidence than a miss on A.
Attack settings are E047's (32 restarts × 30,000 iterations, 4-gram Kneser–Ney model with spaces). Languages are run
in batches of five to bound memory. Seed 63063.

## Outcomes
| Outcome | Rule | Ledger |
|---|---|---|
| **CLAIM** (any language, A or B) | as above | **no factor yet**: a blind reading (E050 style) and a single LOCKED_TEST scoring follow under their own pre-registration; only a confirmed reading moves the ledger |
| **NO CLAIM, validated** | all languages validated, none claims | absence rule: the "other European and unlisted" share of L-alpha-known (0.27 of 0.35) is taken as 0.8 covered by these 50: s = 0.0756, m = 0.2 → **L × 0.94**. C: simple or homophonic substitution of these languages, 0.05 of C → **C × 0.96** |
| partly validated | some languages fail validation | the factor is scaled by the share of languages validated; unvalidated languages are listed as untested |

Why no factor for a CLAIM: E049's Hebrew near miss scored inside the fake range only after the pseudo-Voynich controls
were run (E050). One attack score is never a decipherment.

## Disclosed
- E052's results for its 7 languages and E049/E050's for Hebrew, Turkish, Latin (in the ledger).
- Word counts of the Bible books per language (design counts, used only to drop the three small translations).
- No language model has been built and no attack run for any of the 50.
- The script was exercised in a dry run that builds the task list and sizes and runs no attack. The dry run showed that
  engWycliffe's file set lacks the plaintext test books (0 words), so it is recorded as UNTESTED; 49 languages run.
