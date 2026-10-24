# E052 pre-registration: the validated attack on the rest of the shortlist, plus Romani

Written 2026-10-24, before the run. Script: `experiments/e052_shortlist_attack.py`. LOCKED_TEST is not used. Updates
`reports/LEDGER.md` through the absence rule (`ABSENCE_RULE.md`).

## Languages
The rest of the E042 shortlist, plus Romani, which was added after E051: languages with echo or doubling grammar match
C21, and Romani is the only South Asian language present in Central Europe around 1400.

| Code | Language | Bible | LM books → plaintext books |
|---|---|---|---|
| cs | Czech | ces1613 (Kralice) | OT Genesis–2 Kings → Ezekiel, Psalms, Proverbs, Job, 1–2 Chronicles |
| sh | Serbian-Croatian | srp1865 | same |
| sk | Slovak | slk (NT only) | Gospels + Acts → Epistles + Revelation |
| uk | Ukrainian/Ruthenian | ukr1871 | OT split as above |
| ro | Romanian | ron1924 (Cyrillic) | same |
| it | Italian | ita1885 | same |
| rom | Romani (Carpathian) | rmc | same |

**Letters.** Lowercase, with accents and diacritics removed (č→c, й→и and so on), and the commonest 23 kept, exactly
as in E047's VOY23 class. For Cyrillic and Czech this deletes some rarer letters. The same loss applies to the
known-answer ciphers, so the comparison stays fair.

## Per language: validate first, then Voynich
- **Validation** (same LM, same E047 attack):
  - 2 VOY23 ciphers of real plaintext (fresh keys, 12% spelling slips). A crack needs accuracy ≥ 0.80.
  - 7 controls: 2 copy-generator samples and 5 pseudo-Voynich-A texts (E050's decisive control).
- **T_l** = the midpoint between the lower crack lexrate and the highest control lexrate.
- **VALIDATED** if both ciphers are cracked with agreement ≥ 0.95, **and** the lower crack lexrate is above every
  control.
- **Voynich A,** attacked with the same LM. **CLAIM** requires all of: VALIDATED, agreement ≥ 0.95, lexrate ≥ T_l, and
  lexrate > (the highest control) + 0.05.

## Decision and ledger
| Per language | Consequence |
|---|---|
| CLAIM | Blind reading (as E050) and then LOCKED_TEST confirmation, pre-registered as E053. No factor yet. |
| VALIDATED, NO CLAIM | Absence rule: the language's share of L-alpha-known × 0.2 (m = 0.2) |
| NOT VALIDATED | No conclusion about that language, and no ledger change |

**Shares within L-alpha-known** (from `ABSENCE_RULE.md`): Czech 0.08, Serbian-Croatian 0.05, Slovak 0.03, Ukrainian
0.04, Romanian 0.03, Italian 0.15.
- **Romani was not listed there.** It is given **0.03 now**, taken from "other European and unlisted" (0.27 → 0.24),
  before it is searched. This is disclosed as a late addition.
- **L-alpha-known is 0.35 of L,** so a language's slice of L is 0.35 × its share. **C** gets no update here: E052
  searches L forms only. Substitution ciphers of these languages were not given shares in C.

## What was seen before writing this (disclosed)
- E047–E051 results.
- Which Bibles have Old Testament books (Slovak does not).
- No attack in these languages has been run.
