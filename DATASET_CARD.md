# Dataset card

## 1. Voynich transliteration (System A, Gate 4)
- **Source:** ZL3b IVTFF EVA transliteration, version 3b of 13/05/2025 (R. Zandbergen, updated from the EVMT project),
  as supplied in the handoff DOCX `data/raw/handoff/source_dump/IVTFF Eva.txt.docx`,
  SHA-256 `6aedc059275bc18c0d4db15a6a6c2e851e9f93a7b532cbed907a34c0db69ddb7`. Images of Beinecke MS 408 are public domain.
- **Parser:** `src/vcl/corpus/ivtff.py` keeps raw token, first-alternative EVA reading and flags for `?`, `[a:b]`,
  `{..}`, `@nnn;`, uncertain spaces, locus type, paragraph start/end, folio, leaf, quire, bifolio, illustration,
  Currier language and hand. Derived file: `data/derived/tokens.csv` (39,020 tokens; 35,069 prose).
- **Splits:** physical leaf. LOCKED_TEST leaves fixed in `eval/PROTOCOL_v1.md` (15 leaves, 6,004 prose tokens).
- **Known limitations:** EVA is a glyph transcription, not a phonetic alphabet; segmentation of glyphs (e.g. `ch`,
  `iin`) and spaces is the transcriber's judgment; uncertain spaces (`,`) occur before 2,463 prose tokens.

## 2. Plaintext corpora for the known-answer curriculum (System B)
- **Source:** Project Gutenberg books selected deterministically (one book per author, hashed order, ≤6 per
  language) from the official catalog. Public domain in the USA. Each book's URL, title, author, raw and normalised
  SHA-256 are in `data/raw/corpora/SOURCE_MANIFEST.json`; raw texts are not committed (rebuild with
  `python -m vcl.synthetic.corpora fetch`, which verifies hashes).
- **Languages / families:** Germanic, Romance, Slavic (train families); Uralic, Austronesian, Celtic, Hellenic,
  Semitic, Dravidian, Constructed (held-out families). Middle English is included as a historical orthography.
- **Normalisation:** lowercase, Unicode letters and marks only, single spaces; native scripts kept.
- **Biases:** literary/religious 19th–20th c. prose dominates; small languages have few books and few authors;
  pretrained LLMs have likely memorised parts of famous texts, so agent results are leakage-flagged.

## 3. Benchmark v1 (`data/derived/benchmark_v1/`)
- Built by `python -m vcl.synthetic.benchmark` from `configs/benchmark_v1.yaml` (seed 20261015).
- Splits: `tune`, `test_in`, `test_lang`, `test_enc`, `test_both`, `test_null`; public and secret files separated;
  every file hashed in `BENCHMARK_HASHES.json` and checked by Gate 0.
- Each task: plaintext window, encoder family, key, language, family, Gutenberg id, seed, difficulty and an
  identifiability tag. Every encoded task is round-trip verified with an exact decoder before being written.
