# E010 "Anchors": can semantic anchors identify a key, and is the real anchor set enough?

**Status: no decipherment.** This experiment proposes no reading of any Voynich word. It measures whether the
anchor approach *could* work. Gate 5 is untouched.

Artifacts:
- dataset: `data/derived/anchors_v1/{anchors.jsonl, SOURCES.md}` (built by `experiments/e010_build_anchors.py`)
- power analysis: `experiments/e010_anchor_power.py` → `experiments/results/e010.json`, with per-job rows in
  `e010_rows.jsonl`
- pre-registered zodiac test: `reports/E010B_PREREG.md`, `experiments/e010b_zodiac_months.py` →
  `experiments/results/e010b.json`
- tests: `tests/test_anchors.py`

## 1. The anchor dataset (102 rows)
| tier | definition | usable rows | of which word-level | examples |
|---|---|---|---|---|
| A | meaning written in a known script on the page | 12 zodiac pages (+3 unlocked marginalia, text only) | **0** | month names mars, aberil ×2, may ×2, jong, iollet, augst, septe(m)b(r), octe(m)bre, nove(m)bre, decebre (voynich.nu). Each is page-level only (6–14 candidate words on the E010B inner-ring set, 15–30 labels per page), and nothing says which Voynich word, if any, carries the month. The marginalia (f116v, f66r, f17r) gloss nothing |
| B | ≥2 proposers from independent lineages agree (genus) | 5 | 5 | f2r Centaurea (O'Neill, Holm, Sherwood, Velinska, Bax), f18r Calendula, f32r Mentha, f90r1 Papaver, f29v Nigella |
| C | single proposer or lineage, or contested | 68 | 67 | Bax's f16r juniper, f68r3 'Taurus', f41v coriander, f3v hellebore, f31r cotton, f27r crocus; 61 Petersen-lineage IDs from ZL comments; O'Neill's pepper/sunflower |
| D | visual resemblance only | 0 (f35v stored, LOCKED) | 0 | f35v ivy-type climber: Operation Exemplar certified **L0**, look-elsewhere p ≈ 1 |

14 rows sit on LOCKED_TEST leaves and are stored but excluded everywhere: f9v Viola (would be tier B), f1v,
f35v, 10 Petersen IDs, and f1r. No zodiac leaf is locked. **No anchor anywhere reaches above L0 as evidence of
meaning.** Tier B means only that people agree on what the *picture* shows. Pairing that plant with a Voynich
word (the first word of the page) rests on the unsubstantiated "first word names the plant" conjecture, and the
form the name would take (language, spelling) is unknown.

## 2. Known-answer power analysis (E010)
Synthetic anchors use real plaintext words from tune-role books in de, fr and pl (one per train family). Three
levels of analyst freedom were tested:
- **mono_strict:** monoalphabetic cipher, injective key, edit similarity.
- **verbose_strict:** homophonic cipher plus a local null-modifier verbose layer; many-to-one key that may map
  a glyph to nothing.
- **flexible_anagram:** the same cipher; the key may also map a glyph to a bigram, and scoring forgives letter
  order.

The score is S = mean anchor similarity. The decisive null is the score of keys **optimised** (simulated
annealing with targeted moves, 3 restarts) to fit anchor sets in which every pairing is wrong. There were 200
null fits and 30 trials per cell. **T1** compares the true key against that null. T1 is an oracle test, because a
real decipherer does not have the true key. **T2** compares a key fitted on the real anchors against keys
fitted on wrong anchors. **T3** fits on half the anchors and scores the other half. Random keys were also
tested; nearly any key "beats" them, so they are a misleading null.

**Identifiability frontier.** The table gives the smallest N with power ≥ 0.8 at p < 0.01. ">40" means not
reached at N = 40.

| mechanism | test | r=1.0 | r=0.8 | r=0.5 | r=0.3 | r=0.1 |
|---|---|---|---|---|---|---|
| mono_strict | T1 true vs optimised-wrong | 3 | 5 | 10 | 40 | >40 |
| mono_strict | T2 fit-real vs fit-wrong | 3 | 5 | 10 | 20 | >40 |
| mono_strict | T3 held-out | 5 | 5 | 10 | 40 | >40 |
| verbose_strict | T1 | 5 | 10 | 40 | >40 | >40 |
| verbose_strict | T2 | 5 | 10 | 20 | 40 | >40 |
| verbose_strict | T3 | 10 | 10 | 40 | >40 | >40 |
| flexible_anagram | T1 | 10 | 20 | >40 | >40 | >40 |
| flexible_anagram | T2 | 10 | 20 | 40 | >40 | >40 |
| flexible_anagram | T3 | 20 | 40 | >40 | >40 | >40 |

Key numbers behind the frontier:
- **Fitting inflates scores.** With few anchors, a key fitted to *wrong* anchors scores as high as the true key
  on right ones. At N = 5 the mean null fit is 0.52 for mono, 0.78 for verbose and 0.94 for flexible; the 99th
  percentile is 1.00 for flexible. With flexible scoring and N ≤ 5, a fitted wrong key matches the anchors
  perfectly, which is the signature of past "solutions". The mean inflation of a fitted key over the true key at
  r = 0.1 is +0.38 (mono), +0.65 (verbose) and +0.64 (flexible) at N = 5.
- **Random keys say nothing.** The true key beats random keys at p < 0.01 in almost every cell, including
  r = 0.3–0.5, where it cannot be told apart from an optimised wrong key.
- **Near-miss keys** score smoothly below the true key: mono N = 20, r = 1 goes 0.92 / 0.84 / 0.71 / 0.50 for
  k = 1 / 2 / 4 / 8 swaps. Under flexible scoring the drop is much flatter (0.97 / 0.94 / 0.88 / 0.79), so a
  flexible method cannot localise the key either.
- The grid is not monotone at small N because the number of correct anchors is round(rN) (for example N = 5
  gives 2 correct at both r = 0.5 and r = 0.3).

**Month scenario (tier A analogue).** 12 month anchors, each page-level with M candidate words.

| mechanism | M=1 r=1 | M=1 r=0.5 | M=1 r=0.25 | M=15 r=1 | M=15 r=0.5 | M=15 r=0.25 |
|---|---|---|---|---|---|---|
| mono_strict (T1/T2) | 1.0/1.0 | 1.0/1.0 | 0/0.27 | 1.0/1.0 | 1.0/0.97 | 0/0.33 |
| verbose_strict | 1.0/1.0 | 0.03/0.93 | 0/0.1 | 1.0/0.40 | 0/0 | 0/0 |
| flexible_anagram | 1.0/1.0 | 0/0.03 | 0/0 | 1.0/0 | 0/0.03 | 0/0 |

Page-level month anchors could identify a simple substitution even with 15-way ambiguity, if at least half the
pages really contain the month name. Under verbose or flexible mechanisms, 15-way ambiguity destroys the
practical test (T2).

## 3. The real anchor set on the frontier
Assumed reliabilities (the probability that the anchor pairing is correct *as a word ↔ word-form pairing*):
- **Tier B:** 0.05–0.4. This is P(genus ID right) ≈ 0.5–0.8 × P(the first word names the plant, in a form
  matching the proposed name) ≈ 0.1–0.5. It is an assumption, not a measurement.
- **Tier C:** 0.01–0.15.
- **Tier A** (page level, month present on the page in Voynichese): unknown. E010B found no sign of it.

The real set was simulated at its own size (power at p < 0.01):

| scenario (N, mean r) | mono T1 / T2 / T3 | verbose T1 / T2 / T3 | flexible T1 / T2 / T3 |
|---|---|---|---|
| B+C, rB=0.4 rC=0.15 (N=72, r≈0.17) — optimistic | 0.53 / 0.63 / 0.47 | 0.03 / 0.33 / 0.10 | 0 / 0.03 / 0 |
| B+C, rB=0.2 rC=0.05 (N=72, r≈0.06) | 0.03 / 0.10 / 0.03 | 0 / 0.07 / 0.07 | 0 / 0 / 0 |
| B+C, rB=0.05 rC=0.01 (N=72, r≈0.01) | 0 / 0 / 0 | 0 / 0.03 / 0.03 | 0 / 0 / 0 |
| B only, rB=0.4 (N=5) | 0 / 0.17 / 0.13 | 0 / 0 / 0.03 | 0 / 0 / 0.03 |
| B only, rB=0.8 (N=5) — implausibly reliable | 1.0 / 1.0 / 0.97 | 0 / 0.27 / 0.17 | 0 / 0 / 0.10 |
| tier A: 12 pages, M≈15 | sufficient only if r ≥ 0.5 **and** mono | insufficient at r ≤ 0.5 | insufficient |

**Verdict: insufficient.** The real anchor set does not reach the identifiability frontier under any assumption
that is plausible. It would be **sufficient only if tier B were ≥ 0.8 reliable as word-level pairings AND the
script were a simple substitution with known word segmentation and a known plaintext form of the names.** None
of those three conditions is established. Under verbose or flexible mechanisms, even 80%-reliable tier B anchors
(N = 5) are indistinguishable from fitted wrong keys. Adding the 67 tier C anchors does not rescue this: at
r ≈ 0.06 they add noise, not power. To be distinguishable under a verbose mechanism, the approach would need
roughly **≥ 10 anchors at r ≥ 0.8, or ≥ 20–40 at r = 0.5**, with any flexibility in mechanism or scoring
pushing that further out. Nothing in the published record comes close.

## 4. E010B: pre-registered zodiac test (summary)
The pre-registration was written before any statistic was computed (sha256 `dfb39b9e…8597`, unchanged). The
label lists *had* been viewed while building the dataset, and this is disclosed in the prereg.
- **Counts:** 299 labels: 30 per full page, 15 + 15 on the split Aries and Taurus pages, 29 on f72r2. This
  matches voynich.nu, which also reports 80% hapax among them.
- **H1** (month name in Voynichese near the annotation; 2 same-month pairs and 6 '-bre' pairs): T1 p = 0.19,
  T1/N2 p = 0.17, T2 p = 0.24, search-corrected T3 p = 0.35. Nothing survives Holm.
  - The best searched word-choice gives p = 0.0001 (z = 8.0) against random selections. That number appears
    *only* before correcting for the search: E010B reproduces in miniature how searched "anchors" are produced.
  - Synthetic power: mono 0.75–0.97, homophonic and verbose 0.01–0.11.
  - **Negative for one-glyph-per-letter spellings; uninformative for homophonic or verbose spellings.**
- **H2** (labels are day labels): recurrence O = 34 against a shuffle mean of 40 (p = 0.96). The ordered
  alignment is *below* the shuffle (z = −3.6). Labels resemble other labels on the same page more than labels
  on other pages, which is page-level style, not a repeated day sequence. The test had power 1.0 for every
  mechanism, so the result is **negative**.
  - The requested "other-section labels" null (Na) fires on the real data (z = 6.9). It also fires on 99–100%
    of structure-free controls in 5 of 6 cells, so it is a style confound and not evidence. This was
    pre-declared.

Prior knowledge, not claimed as new: the month names are in a later hand in a form of French (Zandbergen);
labels are 80% hapax; ok/ot prefixes dominate; forum analyses report a per-folio prefix drift; Stolfi found no
alignment between ring text and nymphs.

## 5. Caveats
- The simulation is **generous** to the anchor approach. It assumes a known mechanism family, known word
  segmentation and known plaintext language. Its correct anchors are exact plaintext word forms, and its wrong
  anchors are independent errors. Real Voynich anchors fail on every one of these counts, so the real
  requirement is stricter than the frontier shown.
- The optimiser is a heuristic. A stronger optimiser would raise the wrong-key null and push the frontier
  *outward*, so the frontier is optimistic.
- The 30 trials per cell give a power standard error of about 0.07–0.09 near 0.5. Holm was not applied across
  the E010 grid; it is a power map, not a test family.
- Tier reliabilities are assumptions, not measurements.
- The dataset is not exhaustive: modern plant-ID lists (Sherwood's full list, Velinska, Tucker & Janick's 59)
  were not collected. Adding single-proposer IDs adds tier C anchors, which section 3 shows contribute
  essentially no power.
- No frontier plot was made: matplotlib is not in the environment. The tables above are the frontier.
