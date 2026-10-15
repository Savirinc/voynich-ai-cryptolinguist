# Voynich Research: Experiments 060–062
**Date:** 13 October 2026  
**Input:** User-supplied Zandbergen–Landini ZL3b EVA IVTFF transcription, version 13 May 2025 (`IVTFF Eva.txt.docx`).  
**Status:** No decipherment; no established phonetic or semantic value for any Voynich glyph.

## The research question
Does the script behave as though certain apparent EVA symbols are strokes, contextual allographs, or composite characters rather than independent letters? In particular, test the repeated minim strokes (`i`, `in`, `iin`, `iiin`), connected benches (`ch`, `sh`), and `qo`; and distinguish a genuine allograph hypothesis from harmless statistical compression.

## Data and sampling
- **32,132** confidently parsed running-text word occurrences.
- **206** distinct source folio identifiers (some subpanels), consolidated into distinct numbered leaves for splitting.
- 5 held-out folds, each withholding *entire numbered folios* (recto/verso and subpanels together).
- Word tokens preserve original EVA spelling; uncertainty markers are excluded rather than guessed.
- All tokenizations are reversible. Score is bits to predict the **original EVA word plus end-of-word**, not a reduced spelling.
- Both bigram and trigram hierarchical probability models were tested with fixed smoothing (no test-set tuning).

## Experiment 060–061: Explicit segmentation hypotheses
| Reversible segmentation | 3-gram bits / original word | Difference from raw |
|---|---:|---:|
| Original EVA: letters separate | 11.64040 | — |
| `ch`, `sh` combined | 11.59359 | -0.04681 |
| `in`, `iin`, `iiin` combined | 11.64028 | -0.00013 |
| `ch/sh` + minims | 11.59336 | -0.04704 |
| `ch/sh` + minims + `qo` | 11.59214 | -0.04826 |
| `ch/sh` + `dy/ey` (comparison) | 11.58899 | -0.05141 |
| `ch/sh` + `al/ar` (comparison) | 11.61826 | -0.02215 |

The core *incremental* benefit of grouping the minim sequences **after** `ch/sh` is only ~0.00023 bits/word, and a bootstrap interval across distinct numbered folios includes zero. Grouping `qo` produces another tiny, uncertain difference. In contrast, `ch/sh` is better than single EVA letters by ~0.047 bits/word with a folio-bootstrap 95% interval from -0.055 to -0.038.

### Critical control: change the model's memory
With **two-character** context (a bigram model) the minim and `qo` groupings **do** help considerably:

| Segmentation | Bigram bits / original word |
|---|---:|
| Original EVA | 13.04292 |
| `ch/sh` | 12.87209 |
| `ch/sh` + minims | 12.75390 |
| `ch/sh` + minims + `qo` | 12.61605 |

The dramatic improvement largely disappears when upgrading to a trigram. **Interpretation:** merging pieces can compensate for the model's short memory. That is not evidence that the author regarded them as individual glyphs.

## Experiment 062: Discover units without telling the model
I trained a standard frequent-adjacent-pair-merging algorithm separately on each training fold.

Across **all five folds**, its first sixteen discovered units included `ch`, `dy`, `ai`, `ok`, `ol`, `che`, `sh`, `in`, `ee`, `aiin`, `ot`, `qok`, `ar`, `al`, `or`, `she`. Some units are overlapping/chained, not standalone glyph identities.

| Number of automatically learned merges | Trigram bits / original word |
|---|---:|
| 0 | 11.64040 |
| 4 | 11.59810 |
| **8** | **11.58125** |
| 16 | 11.65876 |
| 24 | 11.69187 |
| 32 | 11.71148 |

The eight-merge result gives ~0.059 bits/word lower predictive error than original EVA (approximately 0.5%). Larger merges worsen performance. This is a modest improvement in text coding, not a decipherment.

**Important:** the system found `qok` as a useful frequent unit, not necessarily `qo` as a standalone letter. The unit `aiin` is also frequent and cannot be assumed to correspond to one sound.

## Direct structural evidence in the transcription
| EVA symbol | Total occurrences | At word end | In word interior |
|---|---:|---:|---:|
| `i` | 10,711 | 7 | 10,698 |
| `n` | 5,707 | 5,561 | 146 |
| `m` | 890 | 848 | 41 |
| `q` | 5,215 | 0 | 51 |

The sharply complementary distributions of `i` and `n` **support testing** a terminal-allograph hypothesis, but they cannot establish that the glyphs have the same underlying identity. A terminal letter in a normal language could also exhibit this pattern. The strong line-final `m` evidence from Experiments 057–059 remains intact, but the precise `m = iin` identity has failed appropriate placebo comparisons (Experiment 058). **Do not automatically replace `m` by `iin` or drop `q`.**

## Literature checked
- René Zandbergen, *Voynich manuscript transliteration* and *Super Transliteration Alphabet (STA)*, https://www.voynich.nu/transcr.html and https://www.voynich.nu/extra/sta.html. Currier treated `in` and `iin` as composite units; EVA represents individual features for reversible transcription. Neither is known to be a correct linguistic alphabet.
- Matlach, Janečková & Dostál (2022), *The Voynich manuscript: Symbol roles revisited*, PLOS ONE, https://doi.org/10.1371/journal.pone.0260948. Authors entertain `n` as a terminal modification of `i` and `m` as an `id`-like ligature, **not** established facts. They caution statistical construction hypotheses can fail when actual text has sequential dependence.
- Bowern and Lindemann (2020), *Character Entropy in Modern and Historical Texts*, https://alumniacademy.yale.edu/sites/default/files/2021-07/Character%20Entropy%20in%20Modern%20and%20Historical%20Texts%20Comparison%20Metrics%20for%20an%20Undeciphered%20Manuscript.pdf. Maximal/minimal grapheme segmentations are useful comparison conditions.

## Direct image audit to run next
The file `voynich_glyph_image_audit_queue.csv` contains **122 records**, including 5 manually prioritized same-folio literal-stem comparisons and 47 odd-position controls. Examples:

- f46v.1 `daiin` vs f46v.3 `dam`
- f34v.9 `oldaiin` vs f34v.2 `oldam`
- f3r.20 `aiin` and `am` in **the same line**
- f8r.19 `kaiin` and `kam` in **the same line**
- f6r.2 `daiin` vs f6r.3 `dam`

**The scans must be checked at native resolution.** Existing screenshots and third-party reduced scans are not sufficient to decide pen joins/minims microscopically. Record whether variants share the *same stem and character geometry*, whether the final stroke is joined, the physical width, and whether original ink permits alternate glyph boundaries. Independent annotation by two reviewers should blind the reviewer to the hypothesized meanings. Compare images against the paleographic alphabet and the Currier/v101/STA encodings rather than using EVA as ground truth.

## Conclusions
**Retain for now:** optional contextual graphic variants, `n` as a possible terminal allograph, `m` as a special positional sign, `ch/sh` as likely composite visual units.  
**Not established:** `m = nn`, `m = iin`, `n = ii`, `q` = negative/plural marker, underlying French, a numeric decoding, or any semantic translation.  
**Do next:** align high-resolution folio scans to the 122 specific loci; produce dual-blind stroke annotations. When annotation adjudication is complete, train an image-conditioned recognizer and repeat all held-out tests using an actual grapheme inventory rather than transcription assumptions.

## Reproducibility
From the same folder as `IVTFF Eva.txt.docx` run:
```bash
python voynich_experiment_060.py
python voynich_experiment_061.py
python voynich_experiment_062.py
```
Dependencies: `python-docx`, Python standard library. No GPU, network, or downloads required.
