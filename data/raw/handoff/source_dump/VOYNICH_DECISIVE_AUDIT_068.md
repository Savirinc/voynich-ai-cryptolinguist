# Voynich decisive audit 068: falsifying a public decipherment candidate

Date: 2026-10-15. Status: **NO VERIFIED DECIPHERMENT**.

## Input and boundaries

- Local source: `voynich_tournament_064/indexed_clean_corpus.csv`, derived earlier from the user's IVTFF transcription. It contains 32,132 conservatively selected running-text word occurrences. It is not the whole unfiltered manuscript and must not be treated as such.
- External candidate: https://github.com/scott-schechter/voynich-decoded/blob/main/publication/01-cipher-system.md (author's claims; not independently confirmed).
- Audit executable: `voynich_solution_audit_068.py`; raw counts: `voynich_solution_audit_068.json`.

## Test 1: Can we verify a specific purported translation by exact written-token frequency?

Candidate assigns `chedy=DEUS` (484 occurrences, 77 folios), `shedy=HEUS` (422, 66), `qol=NON` (138, 36), `daiin=OLEUM` (768, 190), `chol=DAT` (362, 138), `okaiin=FOCUM` (205, 89), `qokol=NOCET` (94, 55), `lchedy=MEUS` (115, 37) and `oly=FLOS` (48, 28).

The assigned words occur as advertised as EVA strings, but their Latin meanings **are not independently verified** by these counts. Treating Latin words as known at training time and calculating fraction matched by a fitted glossary is in-sample vocabulary coverage rather than a demonstration of translation. Likewise, grammar created by rearranging word order after decoding cannot validate the original order without a precommitted rule.

## Test 2: Semantic constraints that a real solution must pass

1. Publish a **fixed, deterministic encoder and decoder**, including null and vowel-insertion policy. No optional, context-free additions after predictions are scored.
2. Publish an untouched set of entire folios and a **locked key**, selected before seeing the candidate translation of them.
3. Translate original line sequences without reordering on the basis of the desired meaning; if an original reading order differs, recover it from predeclared spatial rules alone.
4. Predict the names of independently identified objects, and score exact matches against alternatives and frequency-matched decoy words.
5. Require human-readable, historically attested grammar with transparent treatment of ambiguity and a comparison with shuffled-cipher and adversarial random-baseline decodings.
6. Require independent replication by a researcher not involved in producing the cipher key.

## State of surviving evidence

Earlier experiments report reproducible orthographic/positional patterns: `-m` strongly favored at line end relative to `-iin` in matched stems; initial `q` conditioned on preceding text; Currier A/B differ; picture labels differ from running prose. None assigns any authenticated plaintext word.

The text could encode a natural language, shorthand, a transformation or a nonlinguistic generative system. We have not eliminated the alternatives decisively. More language-model compute may learn style but does not automatically identify meaning.

## New independent audit results

The local script uses exact EVA tokens from the prior conservative corpus. The nine proposed plaintext assignments are **hypotheses**, not independently recovered readings. No false proof of decipherment was produced.

**Decision:** Do not declare this or any alternative scheme solved on the strength of fit to training data. Prioritize fixed-key, blind, semantics-bearing predictions. This report documents a failed verification, not proof that the external author's claim is necessarily false.
