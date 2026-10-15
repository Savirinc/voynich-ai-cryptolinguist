# Voynich Experiment 057: Line-sensitive writing and contextual word beginnings

**Source:** User-provided *IVTFF Eva.txt.docx*, ZL transcription (13 May 2025). An EVA transcription is not an alphabet decipherment or phonetic rendering.

## Research question
Can the physical placement of a written word explain apparent word variants independently of word identity, and does the initial `q` relationship reset across manuscript lines?

## Method
- Read running-text `P`-locus records and word/paragraph markers directly from the DOCX file. Strip inline structural markers (`<%>`, `<$>`, `<->`) without discarding adjacent clear words; skip uncertain segments.
- This corrected parser has 32,132 clear running-text tokens across 206 folios (not every inscribed glyph).
- Split folios deterministically 80/20 using a fixed SHA-256 hash. Determine eligible stems using only the training folios.
- Test same-stem `-m` / `-iin` forms and `qo...` / `o...` forms. Compare models on held-out folios.
- Calculate folio-cluster bootstrapped intervals so adjacent tokens are not treated as statistically independent. All analysis is at the transcription-line level, not direct independent image measurement.

## Result 1: final -m is strongly linked to the end of a written line

In held-out folios, among eligible same-stem pairs, `-m` occurs in:
- 35 / 489 cases **within a line** (7.2%).
- 70 / 119 cases **at an ordinary line ending** (58.8%).
- 7 / 15 cases **at a paragraph ending** (46.7%; too few to compare precisely).

For ordinary line endings versus within-line words, the folio-bootstrap 95% interval for the odds ratio is approximately **8.95–39.29**, median 18.25. Both Currier A and Currier B show the effect, although it is stronger in B. A model containing word stem and Currier variety gives held-out log loss **0.4245**; adding line position reduces it to **0.3103**. Separating ordinary line endings from paragraph endings produces **0.3092**, a small further gain whose folio-bootstrap CI includes zero.

**Interpretation:** Strong evidence of line-position-dependent spelling/abbreviation. Not a demonstration that `m` and `iin` always encode the same meaning.

## Result 2: a control test for specificity

For paired forms in held-out folios:
- `-m` versus `-iin`: odds ratio at line end = 17.52.
- `-m` versus `-in`: 23.48.
- `-in` versus `-iin`: 0.81 (p = .42), not an analogous effect.
- `-r` versus `-l`: 0.80 (p = .41), not an analogous effect.
- `-dy` versus `-ey`: 1.78 (exploratory p = .045), much weaker.
- `-g` versus `-y` had too few test instances to evaluate.

These controls were explored after observing the `-m` pattern, so the p-values for the controls should not be treated as a pre-registered multiple-comparison result.

## Result 3: q/o contextual dependency across line breaks

Among eligible paired forms in held-out folios:
- **Within lines**, `q` is chosen 483 / (483+265) = 64.6% after a preceding word ending `y`, versus 171/(171+430)=28.5% after other endings (unadjusted odds ratio 4.58).
- **Across continuation lines**, `q` is chosen 32/(32+12)=72.7% after `y`, versus 42/(42+41)=50.6% after other endings (unadjusted odds ratio 2.60). Only 127 eligible cross-line observations are available.
- The earlier model comparison (Experiment 054) on held-out folios found **no improvement** from a separate previous-ending × line-break interaction (log loss 0.5673) compared with the simpler preceding-ending + line-position model (0.5669).

**Interpretation:** The `q` relationship is contextual. A special rule that resets across line breaks has **not** passed held-out prediction testing. We cannot confidently tell whether the pattern comes from a cipher, morphology, ordinary word sequencing, or a scribal practice.

## What we can legitimately say

- The surface script has an unusually strong **layout-conditioned** orthographic pattern in the `-m` family.
- The initial `q` family has a **contextual** dependency on the preceding word, but evidence for a line-boundary reset is presently insufficient.
- The most defensible next step is a transducer model that regards line-final `m` as a *candidate* rendering of the same underlying component as `iin` (and perhaps `in`) and compares it against alternatives on genuinely unseen folios.
- No French, Latin, Urdu, Persian, or other-language plaintext has been recovered, and no word is deciphered in this experiment.

## Historical context

The line-final `m` / `iin` possibility is **not newly discovered**; it is described by Claire Bowern and Luke Lindemann, *The Linguistics of the Voynich Manuscript* (2021), and discussed by Voynich researchers. The novelty here is the specific controlled evaluation on the uploaded transcription.

## Reproduction

Execute `python voynich_experiment_057.py` and `python voynich_057_controls.py` with `IVTFF Eva.txt.docx` in `/mnt/data` and the installed `python-docx`, `numpy`, `scipy`, `scikit-learn`. `voynich_experiment_054.py` is included for the earlier line-interaction evaluation.
