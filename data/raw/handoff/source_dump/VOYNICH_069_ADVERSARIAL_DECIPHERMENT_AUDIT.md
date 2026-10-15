# Voynich 069: adversarial test of a published decoding claim

## Scope and status

Tested the *complete available clean running-text corpus* (32,132 tokens, 206 folios) for nine frozen EVA→Latin/Occitan assignments taken from the existing local 068 audit of the public Scott Schechter decoding proposal. This is **not** a test of the entire published glossary, which was unavailable as usable programmatic bytes in this environment. The source's claimed denominator (37,886 tokens in Takahashi EVA) differs from this study's cleaned IVTFF EVA prose denominator. Do not compare the two percentages directly.

Public proposal: https://github.com/scott-schechter/voynich-decoded/; standalone decoder https://raw.githubusercontent.com/scott-schechter/voynich-decoded/main/decode.js. The public decoder uses an exact glossary lookup and a second lookup after stripping selected super-gallows. These steps can yield high coverage without themselves demonstrating a general reversible transcription-to-plaintext cipher.

## Frozen assignments

`chedy=DEUS`, `shedy=HEUS`, `lchedy=MEUS`, `qol=NON`, `qokol=NOCET`, `chol=DAT`, `daiin=OLEUM`, `oly=FLOS`, `okaiin=FOCUM`.

These nine forms occur 2,624 times (8.17% of clean running-text corpus); coverage of them is not evidence they are correct translations.

## Test

For each line of the transcription, count occurrences of nine prespecified adjacent ordered pairs. Generate 1,500 randomized within-line word orderings, preserving the exact multiset of words and line lengths, using numpy generator seed 69021. Report observed count, shuffled expectation, exploratory one-sided permutation p-values. This null model does not preserve prose syntax or word-position effects, and thus cannot alone establish translation. More rigorous matched synthetic corpora and comparison with whole-glossary predictions are required.

## Results

| Pair | Observed | Null expectation | Exploratory p (enrichment) | p (depletion) |
|---|---:|---:|---:|---:|
| DEUS MEUS | 6 | 3.370 | 0.1053 | 0.9627 |
| MEUS DEUS | 6 | 3.434 | 0.1146 | 0.9534 |
| NON NOCET | 0 | 0.115 | 1.0000 | 0.8854 |
| OLEUM FLOS | 1 | 0.436 | 0.3824 | 0.9480 |
| FLOS OLEUM | 0 | 0.451 | 1.0000 | 0.6016 |
| OLEUM FOCUM | 8 | 4.284 | 0.0526 | 0.9773 |
| OLEUM DAT | 6 | 14.364 | 0.9987 | 0.0053 |
| DEUS DEUS | 9 | 11.234 | 0.8308 | 0.2838 |
| HEUS DEUS | 8 | 8.945 | 0.6782 | 0.4550 |

These results are mixed. The finding that OLEUM DAT is underrepresented is noteworthy as a *negative* probe for the claimed assignments but does not refute them. Further, phrase selection is exploratory and some readings may be transcription- or contextual-dependent. No phrase meets an unquestionable semantic validation standard.

## Corpus coverage and differences

Sections are classified by manuscript type, not a language inference. See `voynich_069_results.json` for all section-level counts. Our corpus extracts running text conservatively and excludes labels, whereas the public claim relies on a Takahashi transcription plus different normalization. Any direct 87.8% replication must use the author's actual glossary, source transcription, decoder, and a frozen test set.

## Decisive protocol for the full public decoder

1. **Archive the exact published repository commit** and its transcript, code and glossary. A claimed 87.8% *dictionary hit rate* must not be reported as 87.8% of meaningful text deciphered.
2. Freeze an EVA→plaintext **generative mapping and linguistic rules** on a predeclared set of training folios. A wordlist lookup learned from the same target corpus is not a blind test.
3. Measure actual **token coverage**, semantic/generative rule complexity, and reversibility on held-out pages. Include random words matched on EVA length and frequency, and control glossaries with target-word labels permuted in frequency bands.
4. Require **natural original reading order** and morphosyntactic agreements on independent lines, not post hoc rearrangement.
5. Require at least three **unseen labels / botanically identifiable illustrations** predicted before viewing the visual target.
6. Repeat across independent transcriptions and blind external reviewers.

**Verdict:** Current evidence does not support a decipherment. This is a falsifiable audit, not a claim that the Voynich Manuscript is unsolvable. External agent swarms or other independent LLMs were not actually launched. Their use must not be implied.
