# E042 pre-registration (attack step 2): the language shortlist

Written 2026-10-23, before the run. Script: `experiments/e042_language_shortlist.py`. Working assumption L. This is a
measurement, with no ledger factor; it fixes which languages step 3 attacks.

## Question
Which languages, plausible for the place and date, have the shape we measured in Voynich **Currier A**?
- simple syllables (E027, E040, E041);
- strong suffixing: about 21 endings (E037, E040);
- frequent doubling of words (C9, C13).

## Stage 2a: documented grammar (WALS)
**Source:** WALS v2020.4 (CLDF, CC-BY), from linguists' grammars, not our statistics. The file sha256 values are
recorded.

| WALS feature | Voynich A's shape | Pass |
|---|---|---|
| 12A Syllable Structure | simple syllables | Simple or Moderately complex (**hard filter**) |
| 26A Prefixing vs Suffixing | about 21 endings | Strongly or Weakly suffixing (**hard filter**) |
| 27A Reduplication | words doubled | Productive (full and partial, or full only) = "doubling language" (**reported and used for ranking, not a filter**) |

**Why reduplication is not a hard filter.** E037 showed that Voynich doubles *frequent, ordinary* words, which is
unlike grammatical reduplication (Indonesian). It may be a text-type habit (E031). WALS records grammar only.

**(i) World base rate.** Among all WALS languages coded on all three features: what share pass both hard filters,
and what share also double? Which families and macroareas do the full matches come from? This shows how *rare* the
profile is.

**(ii) The fixed candidate list.** Languages a writer in or near Central Europe, northern Italy or the Alps around
1400–1440 could plausibly have used: learned, vernacular and contact languages, plus two earlier proposals.

| Candidate | WALS entry used | Text (eBible) |
|---|---|---|
| Latin | — (not in WALS) | latVUC (Vulgate) |
| Greek | grk (Modern Greek: approximation) | grcbyz (Byzantine NT) |
| Hebrew | heb (Modern: approximation) | hboWLC (Biblical) |
| Arabic | aeg (Egyptian: the only Arabic coded on all three; approximation) | arb-vd (Standard) |
| German | ger | deu1912 |
| Czech | cze | ces1613 (Kralice) |
| Polish | pol | polubg |
| Hungarian | hun | hun (NT) |
| Italian | ita | ita1885 |
| French | fre | fraLSG |
| Occitan | — | — (no text) |
| Catalan | ctl | — (no downloadable text) |
| Serbian-Croatian | scr | srp1865, and hrv as a second text |
| Slovak | — | slk (NT) |
| Slovene | slo | — (no text) |
| Romanian | rom | ron1924 (Cyrillic) |
| Romani | — | rmc (Carpathian) |
| Turkish | tur | turytc |
| Armenian | arm | — (no text) |
| Yiddish | — | ydd (NT) |
| Dutch | dut | nld |
| English (Middle) | eng (Modern: approximation) | engWycliffe (Middle English, partial) |
| Lithuanian | lit | lit (partial) |
| Ukrainian/Ruthenian | ukr | ukr1871 |
| Albanian | alb | — (no text) |
| Mandarin (Stolfi's "Chinese-like" proposal) | mnd | cmn-cu89s (pinyin syllables as tokens, as in E030) |

**Rules:**
- A candidate is **out at 2a** only if a *coded* hard feature fails. Missing codes never exclude.
- Languages without a text are reported at 2a only.

## Stage 2b: statistics
- **Target:** Voynich Currier A, cleaned (N1: e-runs → e, t → k).
- **Candidates:** every candidate not out at 2a and with a text.
- **Measure:** E033's 8 spelling-independent features (R, types, I_word, top_word, PERS_30, COV_30, type_hapax,
  zipf_slope), on non-overlapping windows of Currier A's token count (up to 10 at random, seed 42042).
  - Hebrew and Arabic vowel points and all accents are removed before splitting words.
- **Scoring:** z = (V − mean) ÷ max(sd, 2%|V|, 0.01). A feature fails if |z| > 3.
  - Fails are counted on all 8 features, and also reported on the 7 without R, since doubling may be a text-type
    effect.
- **SHORTLIST** = candidates with at most 2 fails of 8, ranked by fails and then RMS z. If none qualifies, the verdict
  is **NO CANDIDATE FITS**.

| Result | What step 3 does |
|---|---|
| SHORTLIST | Attack the shortlisted languages, top first, using a known-answer-validated method |
| NO CANDIDATE FITS | No plausible language with a text fits. Next: the closest candidates on the 7 features without R, a check of the untestable languages (Occitan, Catalan, Armenian, Slovene, Albanian), and the picture route (step 4). |

## Limits (stated now)
- **Genre:** Bibles, not herbals.
- **Modern texts for medieval languages,** apart from Latin, Czech 1613 and Middle English.
- **Several WALS entries are approximations** (modern varieties).
- **WALS categories are coarse.** "Moderately complex" includes languages that E024 found outside Voynich's range.
- **A shortlist is a list of languages to attack, not evidence that Voynich is in any of them.**

## What was seen before writing this (disclosed)
- **The WALS feature *coverage* for the candidates** (which features are coded), not the values. The values may be
  known from general knowledge: e.g. German syllables are complex, and Turkish is suffixing.
- **Bible availability on eBible.**
- **Voynich A's values** from E040/E041.
