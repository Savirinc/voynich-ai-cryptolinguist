# FINAL_VERDICT — Voynich MS 408, adversarial decipherment program (15 Oct 2026)

## Verdict
**No candidate reaches Level 3, Level 2, or even enters the semantic challenge.** The highest evidence level attained is **Level 1 (productive writing-system explanation)**, and only partially. No translation, word meaning, phonetic value or language identification is claimed. The one public decipherment examined (Schechter, Latin–Occitan–Hebrew) is falsified as evidence.

## What was falsified (with the single most constraining observation each)
1. **Dictionary-coverage decipherments.** A frequency-ranked dummy glossary matches the 87.8% claim (89.4% vs 89.2%); frozen rules decode 5% of unseen word types; 62% of target forms unattested; word order carries no Latin information (z = −0.47).
2. **Monoalphabetic, homophonic, polyalphabetic substitution of Latin, Old French, Italian, Middle English, Old Occitan, Middle High German (and modern proxies).** h2 = 2.0–2.5 bits vs 3.1–3.4 — invariant under any bijection, and homophony/polyalphabeticity move it the wrong way.
3. **Exact medieval abbreviation of Latin** (128 rule subsets): cannot push h2 below 3.34.
4. **Abjad/vowel-omission encodings** (9 languages × 4 variants): no variant matches h2, length variance and slot rigidity simultaneously; the decoder's apparent signal is equalled by a non-linguistic grille and the recovered keys are as unstable across folds as the grille's.
5. **Spaces-are-not-boundaries.** EVA spaces sit in the true-boundary band of the cross-boundary mutual-information test (0.10–0.16; random spaces 0.98–1.02) and are blind-recoverable at F1 0.73.
6. **Columnar transposition**: produces the "wrong-transposition" signature. **Fixed-rule null glyphs**: no rule yields positive held-out gain. **Positional-allograph merges**: never beat placebo merges.
7. **Verbose cipher of Latin/Italian/Old French as an information source**: the Latin lexicon beats a scrambled-letter lexicon by −0.02 to +0.02 bits/word on dev and blind, at 4× EM budget still −0.035. (Adversarial review downgraded the larger "0.8-bit" gap to a fixed-prior artefact; the zero-information finding stands.)
8. **Zodiac-label semantics** (degree numbers, decans, unique star names, neighbour-copying): all p ≥ 0.07 with planted-structure positive controls recovered at p = 0.002.

## What survives (Level 1, structural — certified by the adversarial reviewer where marked)
- EVA units are real, sharply self-delimited units — but the MI test cannot tell words from syllable-groups (CERTIFIED, with that caveat).
- A content-free character 5-gram conditioned on the previous unit's final glyph and on line-final position predicts untouched blind prose at 11.01 bits/word and reproduces, in samples, the y→q dependence (0.59 vs 0.28; real on blind 0.64 vs 0.21) and the line-final -m effect (0.53 vs 0.13; real 0.41 vs 0.10). Pre-registered predictions P1–P4, P6 passed; **P5 failed** (label ot/ok/op/of-initial share 48.6% vs ≥55% predicted).
- Label vs prose register difference (first-glyph JS 0.139, p = 0.0005; q-initial 0% on blind leaf 72) — CERTIFIED, structural only.
- The two signature context effects generalise to untouched leaves; a reviewer caveat applies: the hypotheses predate the holdout (they came from the user's earlier full-corpus experiments), so this is generalisation, not discovery.

## Observations that remain unexplained
- Why h2 is ~1 bit below any language while Zipf slope (−0.92), TTR and hapax fraction are language-like.
- The adjacent edit-distance-1 rate (0.038): no model reproduces it (best ≤ 0.024). The probabilistic self-citation model put <0.1% weight on copying, so the simple Timm–Schinner mechanism is not favoured either — the near-repeat structure is real but unmodelled.
- Why the y→q rule and the line-final -m rule exist at all (allography, abbreviation, cipher state, or generator) — the structural models reproduce them only because they condition on the defining variables (reviewer downgrade).
- Why zodiac labels are 70% (non-blind) / 49% (blind leaf 72) ot/ok/op/of-initial — the register effect is real but its size varies by page.

## Main limitation
Not compute (every search that had a working positive control converged), not transcription (ZL3b and Takahashi agree on all headline statistics), and not missing languages for the classical cipher families (the entropy invariants exclude them regardless of language). The limitation is **absence of a unique semantic anchor plus genuine underdetermination**: with h2 ≈ 2 bits, ~30 units and rigid positional slots, the text carries roughly half the per-symbol information of alphabetic prose, so any mapping to a language must be many-to-one or context-driven, and the search space of such mappings is large enough that LM-guided search produces language-shaped output from non-linguistic text (demonstrated with the grille and slot-grammar nulls). Two methods (context-dependent substitution; units→syllables) were additionally underpowered — their Voynich results are void, not negative.

## The single future discovery that would most change the prospects
A **verified external text correspondence**: one passage of Voynichese whose content is independently fixed — a known source text copied with the same illustration program (herbal/balneological/astrological exemplar), a bilingual marginal gloss, or a securely dated reuse of the manuscript's text elsewhere. Every statistical approach here converged on the same wall; only an anchor of that kind converts the Level-1 structural model into a decoding test. Second-best: blinded per-figure attribute coding of the archived zodiac images tested leaf-held-out, which is now technically possible with the materials in `workstreams/ws_d_zodiac/images/`.

## Computational exhaustion vs impossibility
This is a finite failure under ~8 CPU-hours, 2 vCPUs, no GPU, with 5 sub-agents, 7–9 language corpora and ~30 falsifiable mechanisms. It does not establish that the manuscript cannot be deciphered.