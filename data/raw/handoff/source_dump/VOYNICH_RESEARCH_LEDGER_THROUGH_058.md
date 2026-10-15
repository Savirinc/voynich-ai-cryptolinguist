# Voynich research ledger: through Experiment 058

**Source of manuscript text:** user-supplied `IVTFF Eva.txt.docx` containing the ZL3b EVA transcription (version 13 May 2025). This is not the original manuscript; it encodes editorial readings and uncertainty. The original Yale folios must be checked for visual hypotheses.

**Status:** NO VOYNICH WORD HAS BEEN DECIPHERED OR TRANSLATED by this research. All proposed spellings are EVA transliterations, not phonetic values.

## Evidence ledger

| Finding | Evidence/experiment | Status | What it does NOT establish |
|---|---|---|---|
| The main text follows constrained glyph adjacency patterns | Experiments 041–043; independently known Voynich feature | Supported | Natural language or cipher identity |
| Initial EVA `q` is nearly always followed by `o` | 043, 049 | Supported | That `q` means negation, plural, or a detached prefix |
| Occurrence of `q` before an `o...` form depends strongly on the preceding word | 044–050, 052, 054–057 | Supported correlation | That q and non-q are two spellings of the *same* word |
| The preceding word's final `y` is an especially useful predictor | 047–050, 052 | Supported correlation | A causal writing rule or a decoded grammatical category |
| `-m` and `-iin` endings show a strong line-position asymmetry | 051–052, 057 | Supported orthographic pattern | That every `m` represents `iin` or the same sound |
| Prefix-stripping models improve word predictability | 058 primary test slight improvement for q, 5 repeated splits worse | NOT robust | `q` can safely be deleted |
| Merging apparent `m/iin` families slightly improves predicting exact original words | 058, all 5 robustness splits | Supported **predictive convenience** | Identity of the paired word forms |
| Randomly pairing `m` and `iin` word forms performs comparably | 058, 50 placebo trials (p≈0.43 for real better) | Negative identity test | That identical stems are the correct mapping |
| Simple repeated numeral spellings at same zodiac positions | 030, 037, 039 | Not supported by tested alignments | Absence of astronomical numbers/degree meanings |
| Drawn zodiac diagrams associate with familiar signs and later Romance-like month names | Folios 70v–73v, published scholarship | Established iconography / annotations | Language of original Voynich text |
| Later month names are a key to Voynichese | Historical investigation, 033–035 | NOT established | `otral = mars` |
| Illustrations can directly ground individual Voynich word meanings | 040, 052–053 and later controlled checks | Not yet established | A vocabulary of plants, stars, gods, or vessels |
| Currier A/B linguistic varieties differ | 015/016, 041–044, 052 | Supported | Distinct natural languages or different cipher keys |

## Experiment 058: What was actually tested

1. Parsed 32,132 confidently transcribed running-text word occurrences; retained uncertainty exclusions and editorial line markers.
2. Split by the **numbered physical folio**, not by token or paragraph: two sides of the same leaf stay in the same split. Primary split: 23,760 training, 2,216 validation, 6,156 test occurrences.
3. From training alone, discovered 158 paired `q+o... / o...` word forms and 53 paired `...m / ...iin` forms, requiring ≥2 training occurrences per form. Their union collapses 208 distinct training surface types.
4. Compared a baseline surface-word model against reversible models predicting a *family* **and the exact original surface form**. This prevents an unfair gain just from deleting rare spellings.
5. Tested random frequency-stratified merges as placebos, and repeated evaluation across five additional leaf splits.

**Primary test:**

| Model | Test bits per word, lower better | Gain versus baseline |
|---|---:|---:|
| No merging | 11.34276 | 0 |
| Merge `q` pairs | 11.34150 | 0.00126 |
| Merge `-m/-iin` pairs | 11.33200 | 0.01076 |
| Merge both | 11.33027 | 0.01249 |

**Five independent alternative leaf splits (fixed model parameters):**

| Split | Raw | q pairs | m pairs | Both |
|---|---:|---:|---:|---:|
| 1 | 11.38791 | 11.40041 | 11.37639 | 11.38932 |
| 2 | 11.80559 | 11.81896 | 11.80161 | 11.81500 |
| 3 | 11.58184 | 11.58352 | 11.57090 | 11.57208 |
| 4 | 12.23735 | 12.24731 | 12.23507 | 12.24494 |
| 5 | 11.43837 | 11.44247 | 11.43005 | 11.43377 |

The `m`-merge gained predictive accuracy in 5/5 splits; `q`-merge lost accuracy in 5/5. Even so, the 50 `m`-merger placebos achieved nearly the same prediction error (mean 11.33233 vs actual 11.33200). The real stem pairing was **not statistically distinguishable from randomized pairing** (empirical p≈0.43). Therefore the predictive win should **not** be promoted into a claim of synonymous spellings. For the combined model, 20 randomized controls produced empirical p≈0.048 on the primary split, but the combined model was worse than the unmerged baseline in 3/5 independent alternative splits. Overall evidence for combined normalization is weak.

**Limitations:** Tiny differences in bits per word, a simple word-bigram/character model, imperfect random-pair matching, no manuscript-image reinspection, and no independent natural-language translation. These are exploratory results, not a discovery of semantics. Config values (bigram mixture .15, char-prior .2, surface conditional smoothing 3) were chosen on the primary validation set; fixed on the five robustness checks.

## Next decisive research tasks

**059. Glyph & allograph audit:** Extract high-resolution Yale folios. Compare actual strokes of EVA `i`, `n`, `m`, gallows, `ch` and `sh` by position. Crucial: distinguish true graphemic similarity from artifacts of EVA transliteration. Store measured bounding boxes and uncertainty.

**060. Boundary-sensitive writing model without assumed lexical equivalence:** Predict `-m`, `-iin`, `qo`, `o`, `ch`, `sh` from preceding context and line position while treating underlying word identity as latent. Compare cross-folio original text probabilities and **reversible placebo operators**, not just compressed vocabulary sizes. Try multiple probabilistic models and calibrate against 15th-century Latin/French/Occitan/German manuscript transcriptions.

**061. Blind semantic anchor challenge:** Use central zodiac pictures, dated medieval descriptions, and independently verified pictorial correspondences to pre-register predictions for original Voynich labels, then evaluate hidden folios and annotated images. The readable month names, written in a later hand, are not a bilingual text.

**Breakthrough criterion:** One compact rule set must predict unseen original spellings **and** independently identify the meaning of several unseen labels or a coherent short passage. Merely reproducing spelling statistics is not decipherment.

## How to rerun

Install `python-docx` and `numpy`. Place `IVTFF Eva.txt.docx` alongside `voynich_experiment_058.py` under `/mnt/data`, or edit the constant `P` in the script.

```bash
python voynich_experiment_058.py
VOYNICH_058_SEED=1 VOYNICH_058_NULL_TRIALS=0 VOYNICH_058_M_NULL_TRIALS=0 python voynich_experiment_058.py
```

The second command changes the leaf split; five such variants were saved as `voynich_058_cv_1.json` through `_5.json`. If rerun in the same location it may overwrite the generated result files.
