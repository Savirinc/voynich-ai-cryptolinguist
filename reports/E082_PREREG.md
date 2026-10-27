# E082 pre-registration (Hebrew campaign H5): other languages written in Hebrew letters

Written 2026-10-27, before the run. Script `experiments/e082_hebrew_script_languages.py`; output
`experiments/results/e082.json`, `e082_run.log`; report section in `reports/HEBREW_CAMPAIGN.md`.

## Form H5
"Hebrew in some form" includes other languages written in Hebrew letters by Jewish scribes. Yiddish was searched in
E063 (no claim). E082 adds the two medieval ones with texts available: **Aramaic** (Targum Onkelos, Torah) and
**Judeo-Arabic** (Saadia Gaon's Tafsir, Torah, Paris 1893 edition). Ladino and Judeo-Italian texts were not found in
the eBible catalogue or Sefaria and remain untested.

## Texts
Downloaded 2026-10-27 from the Sefaria API, one line per verse, 5,845 verses each (Onkelos 83,421 words; Tafsir
81,570), stored under `data/external/hebrew_script/` (gitignored; Onkelos version CC-BY-NC, used for research only).
Marks removed with E052 `norm`. Model from the first 62% of verses (Genesis–Leviticus), plaintext from the rest
(Numbers–Deuteronomy).

## Procedure and rules
Exactly E080/E063: 23 commonest letters; per language 2 cracks, 2 generator + 5 pseudo-Voynich-A controls, Voynich A,
5 pseudo-Voynich-B controls, Voynich B; 32 restarts × 30,000; seed 82082. VALIDATED / CLAIM rules as E063.
| Outcome | Next | Campaign |
|---|---|---|
| CLAIM | blind reading, then a LOCKED_TEST prediction | none until confirmed |
| NO CLAIM, validated | — | H5 excluded for Aramaic and Judeo-Arabic on A and B, within H1's scope |
| not validated | — | that language untested |

## Disclosed
E080, E081 and the H4 count. Text sizes above. No attack has been run with these languages. One attempt.
