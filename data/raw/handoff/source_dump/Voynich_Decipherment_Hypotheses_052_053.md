# Voynich decipherment: hypothesis distillation (Experiments 052–053)

Date: 13 October 2026
Source: user-supplied *IVTFF Eva.txt.docx*, ZL transliteration v3b (13 May 2025). No translations claimed.

## Analyzed corpus
30,161 clean prose token occurrences from 206 folios; 872 clean illustration-label occurrences. Manuscript glyphs are rendered here in EVA transcription, which is not a phonetic alphabet. Uncertain or edited tokens are excluded; folio-level train/test split from SHA-256 `voynich052:<folio>` modulo 5, with 165 training folios and 41 withheld folios.

## Hypothesis A: final `-m` as a line-conditioned scribal variant or abbreviation

Test paired `stem+m` and `stem+iin`, with stems selected only in training. Baseline: logistic model given stem identity + Currier language A/B. Candidate model adds whether the token ends a transcribed line.

* Matched stems: 47
* Test occurrences: 599 from 39 withheld folios
* At a line end: `-m` on 66 / 115 = 57.4%; elsewhere: 34 / 484 = 7.0%
* Held-out error: 0.4177 baseline → 0.3052 with line-position feature
* 95% clustered bootstrap interval for error reduction: 0.0477 to 0.1822
* Examples: `daiin/dam`, `aiin/am`, `qokaiin/qokam`, `okaiin/okam`
* Negative control `-in/-iin`: no analogous line-final effect (unadjusted held-out p ≈ 0.31); `-r/-l` also negative (p ≈ 0.21). `-dy/-ey` shows a smaller exploratory effect (p ≈ 0.035).

Interpretation: line position strongly influences `-m` form, and a specific truncation/abbreviation is plausible. This **does not prove** `m` is phonetically equivalent to `iin`; note `-m` is also line-finally favored against `-in`.

## Hypothesis B: initial `q` is a context-dependent surface modifier

Compare exact paired `qo...` and `o...` forms, predicting selection after a preceding word ending `y` within the same transcribed line. Baseline model uses remaining word form and Currier variety; candidate adds previous-word-final `y`.

* Matched word forms: 174
* Test occurrences: 1,291 from 39 withheld folios
* After preceding `y`: `q` on 469 / 723 = 64.9%; other contexts: 164 / 568 = 28.9%
* Held-out error: 0.6153 → 0.5688
* 95% folio-bootstrap interval for improvement: 0.0268 to 0.0592

Interpretation: the next word's written form is context-dependent. This does **not** establish a negation, plural, or other specific meaning of `q`.

## Hypothesis C: writing register selects the prefix

Compare 872 isolated labels against 30,161 prose tokens. Word-initial `q`: 9/872 = 1.03% in labels versus 5038/30161 = 16.7% in prose. Of the 485 o-initial label occurrences, 240 have a `q`-prefixed counterpart attested in the prose somewhere in the manuscript. A conditional analysis of 129 informative shared stems gives a pooled label-versus-prose odds ratio of ~0.0196 for the q-form (95% CI 0.00768–0.0502). This is a strong *register association*, not a translation. Confounds include illustration section and the possibility that stand-alone labels have a distinct lexicon.

Same-folio illustrative match: on f84r, an illustration is labeled `okedy`, and `qokedy` recurs in nearby prose. But both forms are common elsewhere; the match alone is not a semantic anchor.

## A compact operational theory

A *surface transducer* is now a more useful working model than direct letter-substitution alone:

1. Start with a candidate underlying form (not yet decoded).
2. Choose a q/o onset variant influenced by previous-word context and writing register.
3. Choose a shorter m-ending variant, partly influenced by line layout.
4. Transcribe the resulting manuscript glyph sequence.

These factors could represent scribal conventions, grammar, or cipher rules, and may not share one origin. We must not equate the model's latent forms with proven spoken words.

## Next decisive semantic tests

1. Independently annotate the actual Yale images for f84r, f82v, and f99v: exact label → object or figure; mark uncertain identifications explicitly.
2. Withhold whole folios. Fit a model only to *visual label ↔ prose* links from the remaining folios, allowing q-normalization only when supported by data, and test whether it predicts label/prose associations on withheld folios **better than frequency-matched shuffled labels**.
3. Compare a compact finite-state transducer to an equally complex conventional language model; score bits per EVA glyph on unseen folios, with a complexity penalty.
4. Attempt historical-language decoding only after establishing nontrivial semantic anchors. Old French/Occitan/Latin/German are competitors, not presumed plaintext.

## Key limitations

* This is analysis of a *transcription*, not direct paleographic analysis of Yale image pixels.
* Transcription 'line ends' have not been independently rechecked against all manuscript images.
* Folios, Currier dialect, subject matter, and layout can interact.
* Correlation with page position is not itself cryptographic evidence.
* Surface normalization can reduce the apparent vocabulary without recovering meanings.

To reproduce: `python voynich_experiment_052.py` and `python voynich_experiment_053.py`, placing the original DOCX in the same directory. Requires `python-docx`, `numpy`, `scipy`, `scikit-learn`, `statsmodels`.
