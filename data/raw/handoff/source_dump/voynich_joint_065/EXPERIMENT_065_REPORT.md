# Voynich Experiment 065: Joint structural model tournament

**Verdict:** the full manuscript has stable, predictable context-sensitive writing regularities. A model conditioned on transcription variety, annotation register, line endings and preceding-word endings improves held-out exact EVA prediction and reproduces several manuscript-level properties. **No language, cipher key, phonetic value, numerical names or decoded word is established.**

## Data and experimental protections

- Source: ZL3b-n IVTFF EVA version 3b (13 May 2025), user-supplied transcription. This run reused the conservative index built in Experiment 064; it did not re-OCR the original Yale images.
- 33,007 clean words (32,132 running words plus 875 isolated illustration labels), on 102 numbered physical leaves. Some disputed, unknown, or oddly segmented tokens were excluded.
- Five deterministic held-out folds grouped by physical leaf, not independent words. Fold sizes vary substantially. ALL reported prediction losses score the **actual original EVA words**, not rewritten normalized aliases.
- The Currier A/B label is **researcher-assigned on the full manuscript**; it is an oracle side-information feature, not an independently predicted property of unseen pages. We separately report a no-Currier ablation.
- Manuscript line-ending flag and picture-label versus prose type are supplied as observable layout annotations (not predicted by the model). This benchmark is *conditional transcription modeling*, not automatic decipherment.

## Exact held-out prediction scores

| Model | Weighted bits / original word | Improvement versus glyph-only | Wins across five folds |
|---|---:|---:|---:|
| Glyph trigram only | 11.72910 | +0.00000 bits saved | baseline |
| Plus Currier A/B + caption/prose category | 11.44372 | +0.28538 bits saved | 5/5 |
| Plus line-end position | 11.41132 | +0.31778 bits saved | 5/5 |
| Plus preceding-word final y | 11.32997 | +0.39913 bits saved | 5/5 |

The strongest model saves **0.39913 bits per word** (3.40% of glyph-only prediction error). This is a structural forecast improvement, not recovered semantics.

## Placebo controls: wrong context should not help

| Context supplied to the trained model | Weighted bits/word |
|---|---:|
| True previous-word ending and line-end flag | 11.32997 |
| Preceding-word ending shuffled within leaf/register | 11.50801 |
| Line-end flag shuffled within leaf/register | 11.54017 |
| Both shuffled, mean of three seeds | 11.71287 |

Both individual context shuffles and the joint shuffle increased test loss in **all five folds**. Shuffling preserves approximate frequency distributions locally and breaks the meaningful associations. These are validation controls, not a null model for possible historical languages.

## Ablation: how much depends on researcher-assigned Currier A/B?

| Model | With Currier labels | Without Currier labels |
|---|---:|---:|
| style | 11.44372 | 11.71700 |
| layout | 11.41132 | 11.65951 |
| context | 11.32997 | 11.57675 |

With Currier assignments suppressed, the full context model achieves **11.57675 bits/word**, still better than the **11.72910** glyph-only baseline. Its extra gain with Currier known is *not* an independent, blind discovery of two historical languages.

## Posterior predictive test: can the models reproduce the manuscript?

On fold zero only, each model generated two word streams in held-out line/layout slots. Unlike mere next-character accuracy, this checks whether generated text resembles several real corpus statistics. For the context model, previous-word conditioning used the **generated** preceding words, not real unseen transcript words.

| Diagnostic | Glyph-only | With register | With line-end | Full context | Better |
|---|---:|---:|---:|---:|---|
| Glyph frequency distribution (JS bits) | 0.0017 | 0.0013 | 0.0016 | 0.0014 | style |
| Initial/medial/final glyphs (JS bits) | 0.0044 | 0.0027 | 0.0035 | 0.0025 | context |
| Word lengths (JS bits) | 0.0230 | 0.0249 | 0.0232 | 0.0233 | raw |
| Previous-y → initial-q effect (absolute rate error) | 0.3807 | 0.4192 | 0.3959 | 0.1468 | context |
| Line-end → final-m effect (absolute rate error) | 0.1076 | 0.0932 | 0.0361 | 0.0349 | context |
| Currier A/B bigram divergence (absolute error) | 0.0748 | 0.0071 | 0.0038 | 0.0026 | context |
| Caption/prose q separation (absolute error) | 0.1624 | 0.0283 | 0.0041 | 0.0103 | layout |

**Important failure:** the full context model still understates the preceding-`y`/initial-`q` effect. The held-out observed gap was **0.3992**, but generated-text context models averaged **0.2524**. The generated word-length distribution is also imperfect. We have not reproduced the whole mechanism.

## Historical-language comparison: not yet executed at corpus scale

Authenticated public corpora were located, including Old French (`OpenMedFr/texts`) and Old Occitan/Gascon (`UD_Old_Occitan-CorAG`), but direct machine-readable downloads into this analysis environment failed. These repositories also differ from the Voynich manuscript in genre, date and editorial orthography. Consequently **there is no honest result ranking Old French, Latin, German, Occitan, Arabic, Persian or a constructed code**. We did not silently replace historical corpora with invented samples, modern dictionaries, or EVA-to-Latin string matches.

Once corpora are accessible, use a split-by-document, era/genre-matched set of historical texts and compare: monoalphabetic substitution, many-to-one symbols, syllable/ligature encoding, positional allographs, word-boundary changes, context-sensitive transducers, and a grammar-free generator. Each mechanism must be fitted ONLY on training material, evaluated on held-out sections, and checked against the same seven joint signatures above. Chance similarities in the month annotations are not sufficient.

## What stays in the evidence ledger

| Claim | State | Reason |
|---|---|---|
| Word form depends on previous word ending | **Survives as a statistical property** | Improves unseen exact-word predictions; true metadata beats shuffled metadata |
| End-of-line spelling variation | **Survives as a statistical property** | Line flag helps original-word prediction, and simulations approach the observed final-m difference |
| A/B text variety | **Survives as a text distribution distinction** | Strong predictive difference when assignments are supplied; not proof of different plaintext languages |
| Captions/prose register distinction | **Survives as a writing difference** | Generation captures much of q scarcity in labels |
| `q` means negation, plural, or is always deletable | **Unproven / automatic deletion rejected earlier** | Predictive value does not reveal meaning; earlier placebo normalization failed |
| `m` means `iin`, `n` means `i`, or minims are single letters | **Unproven** | Original scan stroke audit and specificity controls inconclusive |
| Zodiac label words are numerals | **Not supported in simple form** | Earlier cross-sign tests did not survive all controls |
| `otral` means `mars` | **Unproven** | Later Romance annotations do not constitute bilingual translations |
| French, Latin, Occitan, German, Persian, Arabic underlying plaintext | **Open; not ranked** | Authentic corpora and cipher modeling have not yet been jointly validated |
| Structured non-semantic word generator | **Not excluded** | A model can reproduce structural features without yielding meaning |

## Next decisive experiment

Construct a pre-registered **image-text holdout**. Freeze a set of ten well-identified, high-resolution diagram items and historical named image-degree comparisons, then train hypothesized language/encoder mappings on other folios. Predict held-out text or semantic attributes *before* inspecting them. Repeat the same procedure with a structured no-semantics generator. A genuine externally verified semantic prediction would count as progress toward decipherment.

## Reproduction

Unzip the project into `/mnt/data/`, preserving the two sibling directories `voynich_tournament_064/` and `voynich_joint_065/`. Run:

```bash
python /mnt/data/voynich_joint_065/run_joint.py
python /mnt/data/voynich_joint_065/context_placebos.py
python /mnt/data/voynich_joint_065/currier_ablation.py
python /mnt/data/voynich_joint_065/build_report.py
```

You need `numpy`, `pandas` and the standard Python library. The supplied conservative input table is derived from the user-provided IVTFF source, included for provenance. Results are not evidence of successful decipherment.

### Public sources

- Yale Beinecke Manuscript 408: https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript
- Open Medieval French texts: https://github.com/OpenMedFr/texts
- Old Occitan Corpus (CorAG): https://github.com/UniversalDependencies/UD_Old_Occitan-CorAG
