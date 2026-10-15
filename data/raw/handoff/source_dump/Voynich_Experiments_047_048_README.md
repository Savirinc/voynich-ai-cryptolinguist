# Voynich experiments 047–048: word ending → next word q- onset

Input: user-provided IVTFF EVA-2.0 ZL v3b transcription, 2025-05-13 (`IVTFF Eva.txt.docx`).

## Dataset and operational target

The parser retains confident lower-case 2–20 character tokens in line-transcribed positions matching `<folio.line,...>` in IVTFF. It studies the binary choice in an *eligible subset* of words: surface forms beginning `qo...` versus `o...`, with at least 3 letters in the common remainder. Across all folios 9,081 eligible tokens are available; 1,619 from 36 entire held-out folios. Other words, labels and uncertain readings are outside the evaluation. The models DO NOT infer sounds or meanings.

## Experiment 047: prior word features on held-out folios

Log loss (lower is better):

- Current word stem + Currier variety: 0.60293
- Also previous-word first character: 0.59052
- Also previous-word last character: 0.56280
- Also previous-word last 2 characters: 0.56230
- Previous-word shape features: 0.55054
- Previous-word shape + exact identity: 0.54496

AUC for the first and last character models: 0.74414 vs 0.77724; full word-shape model 0.78957.

## Experiment 048: one-character rule and adjusted analysis

A binary indicator that the previous word ends with EVA `y` reduces held-out log loss from 0.602928 to 0.573598. A full categorical previous-ending model reduces it to 0.562805. Across 3,000 bootstrap samples of entire held-out folios, the `y`-indicator gain had a 95% interval of 0.011015–0.049078 log-loss units; the entire previous-ending gain had interval 0.019213–0.062563.

Observed `q` proportion for the eligible words following previous words ending `y`: 0.62914 (n=4,352), versus `r`: 0.19268 (n=929), `n`: 0.23214 (n=1,288), `l`: 0.35242 (n=908).

Mantel-Haenszel odds ratio for preceding `y` versus other previous endings, stratified by *current remainder* and Currier variety, excluding line-initial cases:

- Full corpus: OR 4.3600, 95% CI 3.8806–4.8987, across 290 informative strata (n=6,443)
- Held-out folios: OR 4.6291, 95% CI 3.3303–6.4345, across 80 informative strata (n=897)
- Currier A: OR 2.4214, 95% CI 1.8241–3.2143
- Currier B: OR 4.9141, 95% CI 4.3229–5.5862

This is a statistical association, not evidence that q stands for a known morpheme, nor a decipherment. Not all manuscripts share the same transcription certainty. The automated parser excludes ambiguous strings and is not a hand-verified, whole-text diplomatic transcription.

## Historical precedent

Prescott Currier reported in 1976 that some Voynich word endings change the distribution of the initial glyph in the following word, especially in Currier B. Original presentation: https://voynich.nu/extra/curr_main.html. These results are modern remeasurement and predictive validation, **not discovery of an entirely new manuscript feature**.

## Reproduce

Requires Python, `python-docx`, numpy, scikit-learn, statsmodels, and source DOCX in `/mnt/data/IVTFF Eva.txt.docx` (change DATA path in scripts as appropriate).

`python voynich_experiment_047.py`
`python voynich_experiment_048.py`

## Next high-value falsification

1. Verify that word boundaries and `y/q` pairs survive image-level checks against Yale scans.
2. Compare with matched-size medieval French, Latin, and German samples, under independently specified hypothetical transformations. Do not infer French from this effect alone.
3. Build and test compact finite-state encoders with terminal-conditioned prefix selection; compare against manuscript section-conditioned character baselines and synthetic copy-edit generators.
4. Use visual zodiac labels as a separate held-out semantic validation dataset before assigning translations.
