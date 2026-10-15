# VOYNICH RESEARCH CONTEXT: COMPLETE HANDOFF

## Source status
- **Original attached materials:** see `source_dump/`, and SHA-256 hashes in `MANIFEST.json`. These include the original `IVTFF Eva.txt.docx`, scripts, JSON results, archived experiment packages, and image screenshots.
- **Experiments 001–069:** material in this handoff is not a uniform 69-step audited research project. Some experiment numbers have no local file; some archives overlap; scripts vary in rigor. Verify before reuse. The 064 and 066 archives each include `indexed_clean_corpus.csv`.
- **External Codex and Claude runs:** their complete repositories are **NOT attached**. Their findings below are **user-reported**, not independently rerun in this package. Import original repositories and run the tests before treating them as validated.
- **No verified translation** of a Voynich word, sentence, or passage has been achieved.

## Corpus
- Original: `IVTFF Eva.txt.docx`, ZL3b IVTFF EVA transcription. EVA is a glyph transcription, not a phonetic alphabet.
- A conservative cleaned extraction was reported to contain 32,132 running-text tokens on 206 folios and 875 label tokens; counts depend on parsing rules.
- Physical-leaf, quire, section, Currier, hand, transcription-variant and figure labels must remain in metadata. Audit uncertain tokens and source provenance.

## Most important earlier structural findings (ChatGPT-run; audit source scripts)
- Strong contextual `y`-final preceding word to `q`-initial next word effect. The `q` is followed by `o` for the overwhelming majority of initial-q words. Naively removing `q` worsened held-out prediction.
- Strong line-final `m` preference relative to `iin`-final forms (held-out odds ratio reported near 18–20), but **no proof** that `m` and `iin` are equivalent glyphs or mean the same thing.
- Glyph-unit candidates `ch`, `sh`, `qo`, `ai`, `dy`, `in`, `aiin`, etc. are statistical groupings, not established phonemes/syllables.
- Currier A/B and prose/label distributions differ; label-initial `q` much rarer than prose-initial `q`.
- Experiment 065 5-fold exact-word prediction: glyph trigram 11.7291 bits/word; plus Currier/text type 11.4437; plus line position 11.4113; plus preceding-word ending 11.3300. Predictive improvement **does not imply semantics**.
- Experiment 066 previous-word contextual `q` log loss improved to 0.5513 nats from 0.6186 baseline; second-previous-word features gave no further gain.
- Zodiac labels/figure counts and order did not yield validated meanings; later month annotations are not original script.
- Experiments 068–069 tested some claimed Latin–Occitan glossary entries; no genuine decipherment. Note 069 tested a small fixed subset of words, not the entire third-party decoder.

## Codex findings, reported by user, not rerun here
- Scott Schechter Latin–Occitan glossary-based decoding reproduced ~89.2% coverage with 4,063 entries; frequency-ranked arbitrary meanings achieved ~89.4%; 1,784 entries hapax.
- Frozen decoder covered only ~5% of previously unseen word types on held-out folios.
- 583/947 tested target words unattested in examined Latin/Old French corpora; 25/36 claimed NOCERE conjugations judged invented. Non-attestation is not categorical impossibility.
- Latin bigram rate did not beat line-shuffled output (z=-0.47), while genuine Latin scored ~4× higher. Reverse encoding was circular.
- Conclusion: coverage is not evidence of decipherment. This does not logically disprove each individual gloss.

## Subsequent Claude research, reported by user, not rerun here
- Tested dictionary decipherments; mono/homophonic/polyalphabetic substitutions across tested languages; exact Latin abbreviations (128 rule subsets; h2 floor 3.34); abjads; non-boundary spaces; columnar transposition; fixed nulls; allograph merges; Latin lexicon signal; tested zodiac semantics: no validated decipherment.
- Spaces were in true-boundary band, blind-recoverable F1 ~0.73. Do not assert every space is original/true.
- Latin lexical model versus scrambled lexicon: -0.02 to +0.02 bits/word on dev/blind; -0.035 at 4× EM budget. Null result under that test.
- Context-dependent substitution and units-to-syllable searches failed their own positive controls: **VOID, not falsified**.
- A content-free conditioned character model predicted blind prose at 11.01 bits/word and reproduced y→q and line-final-m effects. Preregistered P1–P4 and P6 passed, P5 failed (label ot/ok/op/of sharing 48.6% versus >=55% prediction).
- Reviewer invalidated an alleged 0.8-bit information gap as a fixed-prior artifact and rejected an earlier held-out framing. Retain corrections.
- No independent semantic anchor found. An effective ~2 bits/symbol estimate was reported in the investigation; verify its exact definition before using it in theory.
- Historical botanical-source investigation: 940 plant drawings in six manuscripts, independent blind coding; known Tractatus family positive control detected. Voynich images did not uniquely match that family; f35v versus Latin 6823 visual resemblance not significant after search correction (71% of shuffled sets produced comparable match). The claimed ivy-on-oak feature was incorrect. Latin ivy passage transcribed as compilation of Dioscorides/Pseudo-Apuleius. No Voynich meaning recovered.
- Veneto alchemical herbals and several inaccessible collections remain untested. Do not call this a comprehensive global exclusion of botanical sources.

## What the new program must NOT do
- Do not train a giant model on ~32k Voynich words and claim spontaneous semantic understanding.
- Do not reward generated Voynich-like strings as if that were translation.
- Do not use the real Voynich corpus as both the source of a fitted cipher hypothesis and its independent semantic confirmation.
- Do not count training on a synthetic cipher and testing the same cipher family as evidence of generalization to an unknown writing system.
- Do not assert an LLM learned reasoning *only* from RLHF; pretraining learns useful representations, and RL with verifiable rewards can improve search behavior.
- Do not imply quantum superposition provides a truth oracle or lets one read all candidate translations.

## Scientifically honest target
Develop an **AI decipherment researcher** that learns methods on many known-plaintext writing-system transformations, validates those methods on *held-out language families and held-out transformation families*, and generates falsifiable hypotheses for Voynich. Without an independent semantic anchor, Voynich results remain structural or speculative, regardless of model quality.
