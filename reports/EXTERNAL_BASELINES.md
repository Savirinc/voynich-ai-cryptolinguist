# External baselines

## 1. NeuroDecipher (Luo, Cao & Barzilay, ACL 2019)

"Neural Decipherment via Minimum-Cost Flow: from Ugaritic to Linear B", arXiv:1906.06718,
code https://github.com/j-luo93/NeuroDecipher @ `480bad2487820e3737fecfdd108214efa769e34b`
(submodules arglib `91b41f5`, dev_misc `6c711b4`). Driver: `experiments/e008_neurodecipher_baseline.py`;
results: `experiments/results/e008.json`; patches: `external/neurodecipher_patches/VCL_PATCHES.md` + `vcl_patches.diff`.

### 1.1 What it solves

NeuroDecipher does **cognate identification between a lost language and a KNOWN, closely related language**.
Inputs: (a) a list of **already-segmented, already-transliterated** lost-language words (Ugaritic in Latin
transliteration; Linear B as Unicode syllabograms, one sign per glyph); (b) a vocabulary of the known relative
(Hebrew; Greek). Output: for each lost word, the known word it is matched to. A character-level seq2seq model
(bi-LSTM encoder, LSTM decoder, a shared "universal" character embedding space) is trained by EM: the E-step
solves a **minimum-cost flow** problem over expected edit distance to pick which lost/known word pairs are
treated as cognates (one-to-one or capacity-k); the M-step trains the seq2seq model on those pairs.
Evaluation = fraction of lost words (that have a gold cognate) whose predicted match is a gold cognate.

It relies on four structural assumptions stated in the paper: monotonic character alignment, sparse
character-level mappings, near one-to-one word-level cognate mapping, and substantial cognate overlap
between the two vocabularies.

### 1.2 Why this is a different setting from our benchmark

Our benchmark (eval/PROTOCOL_v1.md, `data/derived/benchmark_v1`) is **ciphertext-only**: the solver sees a
symbol stream and must recover plaintext/key, with no word list of a known relative, and with explicit
`non_identifiable` tasks and decoys where the right answer is to abstain. NeuroDecipher instead *assumes* a
language family, a word segmentation, a sign inventory and a lexicon of the relative, and it never abstains
(the flow always returns D matches). Its accuracy numbers are therefore **not comparable** to Gate 1/2 character
accuracy and must not be placed in the same table.

### 1.3 How it maps to our gates

- It is a **positive control for the "lost script with known relative" regime**: on real ancient scripts
  where the answer is known (Ugaritic, Linear B) the method should recover a substantial fraction of
  cognates. A pipeline that claims to handle this regime must at least match it on these data.
- Gate 0: satisfied for our reruns (commit hashes, env versions, commands, seeds in e008.json; ledger rows).
- Gate 1 analogue: the paper's 65.9% (Ugaritic noisy) / 84.7% (Linear B) are the reference positive-control
  levels. Our gate threshold (>= 0.90 char accuracy) is a different metric and is not applied here.
- Gate 3 (decoys): **not addressed by the method**. It has no "no relationship" output; run on an unrelated
  language pair it will still return D matches. Any future use must add a decoy control (e.g. shuffled
  known-language lexicon, unrelated language, or a synthetic generator) and calibrate an abstention threshold.
- Gates 4/5: not applicable; it produces word matches, not a validated reading.

### 1.4 What applying it to Voynich would require (NOT done; no Voynich runs)

NeuroDecipher cannot be applied to the Voynich manuscript without assumptions that are themselves the open
questions. Each of the following would have to be fixed *in advance* and is a free researcher choice:

1. **A candidate related language** with a word list (Latin, Italian dialects, Occitan, Hebrew, Czech, ...).
   The method presupposes genetic relatedness with substantial cognate overlap; a cipher, a constructed
   language, or meaningless text violate this and the method will still output matches.
2. **A segmentation into words**: EVA spaces are uncertain (half-spaces), and "words" may not be
   linguistic words at all.
3. **A glyph inventory / transliteration**: EVA vs. other schemes; ligature/allograph merges; the method
   treats each character as an atomic sign with mostly one-to-one sound correspondences.
4. **Character-level monotonic, sparse correspondence**: excludes verbose ciphers, nulls, transposition,
   abbreviation systems and homophony, all live Voynich hypotheses.
5. **A cognate budget D and capacity**: the number of matches to force; strongly affects output.
6. **A decoy protocol and held-out evaluation**: matching any lexicon to any word list yields matches; without
   a null distribution (unrelated languages, shuffled Voynich, synthetic generators from e007) any Voynich
   "result" would be uninterpretable. By our protocol it would be VOID until such controls pass.

Given e007's finding that Voynich's fingerprint is matched both by encoded-language and meaningless generators,
assumptions 1 and 4 are not established, so NeuroDecipher is recorded here as a positive control only.

### 1.5 Licences

| Item | Licence | Handling |
|---|---|---|
| NeuroDecipher code (main repo) | **none** (no LICENSE file; GitHub `license: null`) -> all rights reserved | cloned to `external/neurodecipher/`, **gitignored**; only `VCL_PATCHES.md` + `vcl_patches.diff` tracked |
| `arglib`, `dev_misc` submodules (same author) | **none** | gitignored with the clone |
| vendored `editdistance/` (H. Tanaka) | MIT | gitignored with the clone (unmodified apart from build flags) |
| `uga-heb.no_spe.cog`, `uga-heb.small.no_spe.cog` | **none stated**; Ugaritic-Hebrew cognates of Snyder, Barzilay & Knight (ACL 2010), "obtained from Ben Snyder" per upstream README | moved to `external/neurodecipher_data_private/`, **gitignored, not committed** |
| `linear_b-greek{,.names}.cog`, `linear_b.{minoan,el}.raw` | **none stated**; extracted by the authors from a Linear B lexicon scan on archive.org (paper fn. 3) | same: private, gitignored |
| `test.es-fr-en.toy.cog` | none stated (6-line toy) | private, gitignored |

SHA-256 of the data files are recorded in `experiments/results/e008.json`.

### 1.6 Reproduction results

RESULTS_PLACEHOLDER
