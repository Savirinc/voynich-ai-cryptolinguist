# E026: does Voynich have a compact ending inventory written with its own glyphs?

Pre-registered: reports/E026_PREREG.md (sha256 7448ea4a…). Script: experiments/e026_endings.py. Results:
experiments/results/e026.json, e026_run.log. 800 twin samples. LOCKED_TEST excluded.

## Pre-registered verdicts
| Check | DEV | Currier B |
|---|---|---|
| Positive control (marked compound split ≥ 0.95 in ≥ 90% of samples; DIST separation ≥ 3 sd) | 95%, 44 sd: **PASS** | 95%, 45 sd: **PASS** |
| **Ending rule** (DIST above, NSUF95 within, the 95th percentile of real spelling) | **MARKED ENDINGS** | **MARKED ENDINGS** |
| Families consistent (\|z\| ≤ 3 on SPLIT, NSUF95, DIST) | none | word_drift4 only |

## The numbers
| | SPLIT | NSUF95 | DIST | PAR |
|---|---|---|---|---|
| **Voynich DEV** | 0.81 | **28** | 0.39 | 0.78 |
| Real spelling (word, la/it/fr/de) | 0.62 | 82 | 0.23 | 0.65 |
| Compound twins (E020) | 0.80–0.81 | 69–91 | 0.32–0.34 | 0.41–0.51 |
| Naibbe cipher twins | 0.87–0.93 | 37–52 | 0.33–0.40 | 0.86–0.92 |
| Rugg / self-citation | 0.91 / 0.88 | 18 / 83 | 0.42 / 0.34 | 0.70 / 0.74 |
| Syllable code | 0.19 | 10 | 0.44 | 0.70 |
| Control: marked compound / random compound | 0.64 / 0.88 | 53 / 54 | 0.97 / 0.12 | 0.55 / 0.59 |

The segmenter's top Voynich DEV endings, by token share, are listed below. They are structure only, not readings.
They agree with the suffix classes known since Stolfi.

| Ending | Share | Ending | Share | Ending | Share |
|---|---|---|---|---|---|
| (none) | 0.19 | ar | 0.04 | o | 0.02 |
| y | 0.18 | or | 0.04 | s | 0.01 |
| dy | 0.10 | al | 0.04 | am | 0.01 |
| ol | 0.06 | ey | 0.03 | | |
| aiin | 0.05 | ain | 0.03 | | |
| edy | 0.05 | in | 0.03 | | |

## What it means
1. **Voynich has a small, regular ending set.** About 28 endings cover 95% of suffixed words, against about 82 for
   real Latin, Italian, French and German spelling and 63–91 for our compound twins. Stems take many endings
   (PAR 0.78).
2. **The endings are only partly written with their own glyphs.** DIST 0.39 is above real spelling (0.23) but far
   below a fully marked notation (0.97), and it is the same as every twin built from Voynich glyph pieces (0.33–0.45).
   As the pre-registration warned, MARKED ENDINGS here mostly reflects Voynich's positional glyph habits. It is not
   evidence of meaning.
3. **No family matches on DEV.** Each misses on a different feature:

   | Family | Where it misses |
   |---|---|
   | Compound twins | Right share of words split (z ≈ 0), but far too many endings |
   | Naibbe and Rugg | Split too many words |
   | Syllables | Split too few |

   The one match on Currier B (word_drift4) does not hold on DEV, so it is not taken as a finding.
4. **For Stage B:** the compound route stays open, but with a corrected target. A stem + ending notation would have
   to use about 28 endings (far fewer than Latin's inflections), written partly in their own glyphs. That fits a
   reduced or abbreviated ending system (e.g. scribal suspension marks, or a vernacular with few endings) better
   than full Latin inflection.

   Next, the known-answer test is rebuilt at this profile: a compound code with about 28 ending classes and partly
   marked endings. That test checks whether the stem + ending attack still works there, with controls, before any
   Voynich attack.
