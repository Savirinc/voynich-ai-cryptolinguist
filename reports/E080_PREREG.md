# E080 pre-registration (Hebrew campaign, forms H1 and H2): validated letter attack with Hebrew on Currier B, and with
# Hebrew written backwards

Written 2026-10-27, before the run, at Arham's direction ("I think it's Hebrew in some form or shape ... try all the
possible tests to decode it"). Script `experiments/e080_hebrew_letters_b.py`; output `experiments/results/e080.json`,
`e080_run.log`; report `reports/HEBREW_CAMPAIGN.md` (shared by the campaign).

## The Hebrew campaign (stated once, applies to E080 onward)
No method can prove or disprove "Hebrew in some form" with certainty. The campaign lists concrete forms and attacks each
with a method that is first shown to crack that form:
| Form | Hidden how | Status before E080 |
|---|---|---|
| H1 | one Voynich sign per Hebrew letter (any letter permutation, atbash included; homophones; spelling slips) | Currier A: E049 no claim. **Currier B never attacked with Hebrew** |
| H2 | as H1, every word's letters reversed | never attacked |
| H3 | morpheme code: fronts = Hebrew prefixes, endings = suffixes, bridges = root letters | not attacked (E079: no clean skeleton fit) |
| H4 | vocalised Hebrew syllables, one Voynich chunk per syllable | not attacked |
| H5 | another language in Hebrew letters (Aramaic, Judeo-Arabic, Ladino; Yiddish done in E063) | texts not on disk |
| H6 | Naibbe-type verbose cipher of Hebrew | E062: class fails |
**Proof** of a form requires: a validated CLAIM, a blind reading by Hebrew readers (E050 protocol), and a single
pre-registered prediction of LOCKED_TEST text. **Exclusion** of a form is within its scope only: the attack must crack
the form on known answers, and a miss is recorded with the attack's measured crack rate.

## E080 procedure (exactly E063, Hebrew only)
- Language model from the Hebrew Bible books GEN–2KI (E052's OT_LM), plaintext from EZK, PSA, PRO, JOB, 1CH, 2CH;
  marks removed (E052 `norm`), 23 commonest letters. Variants: **forward** (H1) and **every word reversed** (H2), LM and
  plaintext transformed alike.
- Per variant: 2 cracks (VOY23 ciphers of its own text; E047 encoder), 2 generator + 5 pseudo-Voynich-A controls,
  Voynich A; 5 pseudo-Voynich-B controls, Voynich B. 32 restarts × 30,000 iterations; seed 80080.
- VALIDATED iff both cracks have accuracy ≥ 0.80 and agreement ≥ 0.95 and the lowest crack lexrate exceeds the
  highest A-control lexrate; T = midpoint. CLAIM iff validated, agreement ≥ 0.95, lexrate ≥ T and lexrate > max control
  + 0.05 (A controls for A, B controls for B).

## Outcomes
| Outcome | Next step | Ledger |
|---|---|---|
| CLAIM (any variant, A or B) | blind reading by Hebrew readers, then a LOCKED_TEST prediction, each pre-registered | none until confirmed |
| NO CLAIM, validated | H1 recorded as excluded on A and B within scope (letter substitution with homophones and 12% slips, 23 signs); H2 likewise | recorded in the campaign; the ledger accounting for the whole campaign is done at its end |
| not validated | that variant untested | none |

## Disclosed
E049 (Hebrew on A: no claim; near miss explained by pseudo-Voynich controls, E050); E063 machinery and results (Yiddish
no claim; Arabic B +0.10 over controls). E079 (Hebrew 4th of 62 on skeleton behaviour). No Hebrew attack has been run
on B or on reversed Hebrew. One attempt.
