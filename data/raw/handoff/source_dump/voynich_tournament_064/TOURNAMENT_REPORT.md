# Voynich Experiment 064: Simultaneous hypothesis tournament

**Status:** no lexical meaning, phonetic value, grammatical category, or complete translation established. The objective is to retain **reproducible structural constraints** while eliminating unsupported semantic assignments.

## Source and method

- Primary source: user's **ZL3b-n IVTFF EVA v3b, 13 May 2025** (`IVTFF Eva.txt.docx`), SHA-256 `6aedc059275bc18c0d4db15a6a6c2e851e9f93a7b532cbed907a34c0db69ddb7`.
- Full accessible transcription parsed; conservatively used **32,132** clean paragraph tokens and **875** clean single-label tokens. Symbols marked as uncertain, rare/nonalphabetic and tokens with ambiguous spellings are excluded; totals therefore do not equal manuscript's total sign count.
- Five deterministic folds by physical **numbered leaf**, not individual word. This avoids training on the back of a leaf while testing its front. Folds are unbalanced in size; see results JSON.
- Predictive benchmarks score **original EVA words**, not merely normalized or shortened replacements. Candidate segmentations were pre-selected from earlier exploratory work, so the 'learned eight' list is not a clean externally held-out discovery.
- Zodiac uses **232 unambiguous single-token labels** with **provisional transcription-order positions**, not verified celestial degree order.

## Structural hypotheses that survive

| Test | Baseline loss | Added feature loss | Conclusion |
|---|---:|---:|---|
| q/no-q paired forms, stem + Currier | 0.6174 | 0.5586 | Preceding word final glyph adds predictive information |
| m/iin paired forms, stem + Currier | 0.4062 | 0.3011 | Line end strongly predicts `-m` form |

Log loss values are **natural units**, pooled out-of-fold predictions. They are NOT statements that q means negation or m means iin. `0.778` and `0.838` are the corresponding held-out AUCs.

### Glyph inventory and positions

- `32,132` clean running tokens include `6,846` surface word types; `25` distinct EVA single characters occur, including very rare transcription variants. This is **not** the number of the author's underlying phonemes or letters.
- Initial `q`: 5,164 glyph occurrences start a word out of 5,215 total q occurrences. `98.02%` of q-initial words have `o` as the next symbol.
- EVA `i` is overwhelmingly internal; `n` and `m` overwhelmingly final. See `glyph_position_table.csv` for full positional counts, not just the cherry-picked examples.
- Currier A and B remain different **among herbals only**: Jensen-Shannon divergence of initial two-character frequencies **0.0851 bits**, versus randomized-folio null mean **0.0167 bits**, p = **0.0025** over 400 exploratory permutations. This does not imply distinct languages.
- Isolated labels and prose have a strong register difference: only **8/517** labels vs **1286/5997** prose tokens begin with q, counting only the **36** folios with both genres. Same-folio random allocation expects about **69.0** q labels versus observed **8** (z = -8.68). That controls folio but not vocabulary/genre.

### Alphabet segmentation competition

Five-fold mean **original-word** costs, weighted by test count (bits per word):

|   context | segmentation           |   bits_per_word |   difference_vs_raw |   beats_raw_in_folds |
|----------:|:-----------------------|----------------:|--------------------:|---------------------:|
|         2 | EVA_raw                |         11.6164 |             0       |                    0 |
|         2 | bench_glyphs           |         11.5698 |            -0.04658 |                    5 |
|         2 | common_endings_control |         11.6434 |             0.02701 |                    0 |
|         2 | learned_8              |         11.5619 |            -0.05453 |                    5 |
|         2 | minim_groups           |         11.6187 |             0.00227 |                    2 |
|         2 | qo_and_bench           |         11.5747 |            -0.04174 |                    5 |
|         3 | EVA_raw                |         11.6641 |             0       |                    0 |
|         3 | bench_glyphs           |         11.7621 |             0.09803 |                    0 |
|         3 | common_endings_control |         11.8843 |             0.2202  |                    0 |
|         3 | learned_8              |         11.9302 |             0.26608 |                    0 |
|         3 | minim_groups           |         11.7028 |             0.03866 |                    0 |
|         3 | qo_and_bench           |         11.7897 |             0.12562 |                    0 |

Result: in a two-character context model, pre-selected `ch/sh` chunks help slightly, and eight preselected chunks help somewhat more. But a three-character-context model prefers **unmerged EVA across every fold**. This is evidence that some segmentation gains merely substitute for insufficient model memory. It does not identify true historical letter boundaries.

## Zodiac and proposed reading tests

**Provisional cyclic 5/7/10/15/30 slots** were tested for association with two-character label prefixes. Nulls preserve sign + ring membership; a second, stronger null only rotates whole rings, preserving adjacency. Familywise correction considers all five tested cycle lengths.

|   ordinal_modulus |   observed_MI_bits |   shuffled_null_mean |   shuffled_p |   shuffled_familywise_p |   cyclic_null_mean |   cyclic_p |   cyclic_familywise_p |
|------------------:|-------------------:|---------------------:|-------------:|------------------------:|-------------------:|-----------:|----------------------:|
|                 5 |            0.36681 |              0.35825 |      0.37288 |                 0.77707 |            0.36034 |    0.39853 |               0.80407 |
|                 7 |            0.49638 |              0.48405 |      0.33289 |                 0.74142 |            0.48006 |    0.30123 |               0.67811 |
|                10 |            0.68891 |              0.64587 |      0.10463 |                 0.33456 |            0.64692 |    0.10663 |               0.33822 |
|                15 |            0.91783 |              0.85123 |      0.03266 |                 0.12463 |            0.85444 |    0.04032 |               0.14962 |
|                30 |            1.3956  |              1.31164 |      0.01866 |                 0.06798 |            1.31126 |    0.01599 |               0.06431 |

The 30-position candidate scores **p ≈ 0.016** against uncorrected cyclic null but **familywise p ≈ 0.064**. That is weak exploratory evidence, **not** a decoded 1–30 count, especially since true zodiac-degree zero points remain unresolved. Previous ring-rotation tests also failed robust fixed numeric word identities.

**Proposed readings under challenge:**
- `otral = mars`: meaning not established; original sign/star label and later Roman-script month annotation are different objects. One-letter-one-letter substitution cannot directly map a five-EVA-symbol token to a four-letter French word without other rules, even if the referent were correct. The crib is **not admissible as a fixed truth**.
- `q = not`, `q = plural`, `q = preposition`, `q = contextual code`: all remain semantically indistinguishable from present evidence; only contextual spelling dependency survives.
- `-m = -iin`: matching stems and line-end association survive, but previous experiment 058 frequency-matched placebo merges did **not** validate identity (reported p≈0.43). Do not normalize mechanically.
- Month names such as `mars`, `aberil`, `may`, `jong` are in a distinguishable **later Latin-alphabet annotation**. Their dialect helps identify one manuscript reader, not necessarily the underlying Voynich language.

## Candidate languages: honest status

**No candidate language has won or been ruled out here.** Authenticated full medieval-language corpora were identified in the source manifest, but their full text could not be downloaded to the local analysis runtime. Directly comparing EVA letters to modern French or Latin letters would assume the unknown cipher key and produce unreliable rankings.

Candidate list: Old French (including Anglo-Norman, Picard), Latin, Old Occitan/Gascon, Middle High German, Middle Dutch, medieval northern Italian, Persian, Arabic, and other/hybrid/artificial systems. The competing *writing mechanisms* are even more important: literal substitution, syllabic/transducer, shorthand, positional allography, codebook, and non-semantic generator.

Historical comparison dataset targets with provenance, date and limitations are in `historical_corpus_manifest.csv`.

## Evidence decisions

- **Retain as structural regularities:** strongly position-restricted glyphs; q/qo transition, preceding-character effect, m end-of-line dependency, Currier A/B distribution differences, scarce q in figure labels.
- **Retain without decipherment claims:** hidden compound glyphs, allography, syllabic or context-dependent code, ordinary natural language with unknown spelling conventions, mechanical generation.
- **Weaken or reject as decoding shortcuts:** delete all q's; merge m/iin as proven synonyms; assume zodiac labels are fixed words for one through thirty; treat later `aberil` as a direct bilingual plaintext crib; declare a language because of glyph shape or exact EVA letters.
- **Potential near-signal:** 30-position prefix association did not pass five-test familywise correction. Pre-register geometry and exact statistic before retesting.

## The next decisive computational challenge (pre-registration)

1. Acquire and checksum **four separate historical-language corpora**. Match era and genre where possible. Hold language identities blind during cipher simulation. Test substitution, many-to-one, syllable, reversible context/transducer and a no-language generator with identical model-capacity constraints.
2. Compare exact original-word held-out log loss *and* a jointly calibrated signature of glyph placement, paragraph boundaries, line boundaries, repetition, A/B differences and label/prose differences. No single statistic may decide the winner.
3. Add independent glyph imaging in a blinded sample before choosing EVA ligature mappings.
4. Freeze ten unseen zodiac labels with verified geometry and an independently mapped medieval degree-image lexicon. **Only a successful semantic prediction** on those labels would count as approaching decipherment.

## Reproduction

`python run_tournament.py && python position_controls.py && python label_register_controls.py && python build_report.py`

Requirements: `python-docx`, `numpy`, `pandas`, `scipy`, `scikit-learn`, `tabulate`. Scripts expect user-provided corpus at `/mnt/data/IVTFF Eva.txt.docx`, with the two supplied zodiac CSVs also in `/mnt/data/`. The original source was not altered.

## Limitations

This is one EVA source, not an inter-transcriber consensus. Commas mark possible rather than certain word boundaries; strict tokenization may treat some disputed segments as words. All comparisons are exploratory and many hypotheses were historically suggested rather than fully specified. Statistical fit does not identify semantics or original phonemes. Local historical-language downloads did not succeed in this runtime. No high-resolution independent glyph segmentation was performed in this experiment.
