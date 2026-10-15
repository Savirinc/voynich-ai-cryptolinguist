# EXPERIMENT_LEDGER — every experiment, hypothesis, metric, control, verdict
Rounds: R1 = round 1 (Takahashi corpus, full-corpus statistics — NOT held-out; see WS-E), R2 = round 2 (ZL3b lossless corpus, blind leaves excluded, leaf-level dev folds), B = one-shot blind challenge.
| ID | Hypothesis / mechanism | Script | Metric | Control | Result | Verdict |
|---|---|---|---|---|---|---|
| R1-1 | Schechter glossary = decipherment (87.8%) | code/audit_gloss.py, phase2_adversarial.py | coverage; held-out unseen-type decode; lexicon attestation; bigram order test | top-K frequency dictionary; shuffled meanings; within-line shuffle | 89.2% vs 89.4% dummy; 5% unseen types; 583/947 unattested; z=−0.47 | FALSIFIED |
| R1-2 | Mono/homophonic/polyalphabetic substitution of 7 languages | phase3_fingerprint.py, phase3_cipher_families.py | h1,h2,IoC invariants | 7 corpora | h2 2.0–2.5 vs 3.1–3.4; IoC more skewed than plaintext | FALSIFIED |
| R1-3 | Verbose cipher, unit→letter | code/cipher_search.py | words≥5 attested | positive control 85–92%; random key 0% | Voynich 0.2–7% | UNSUPPORTED |
| R1-4 | Zodiac/pharma/plant semantics of Schechter output | phase4_semantic.py | sign-name hits; ingredient hits | — | 0/10 pages; 1/93 jars | FALSIFIED |
| R2-corpus | Lossless ZL3b corpus + frozen holdout | code/build_corpus.py, freeze_holdout.py | — | — | 35,777 tokens; blind 3,019 tokens; sha256 recorded | — |
| WS-A-1 | EVA spaces are not plaintext boundaries | ws_a_cryptanalysis/m1_boundaries.py | cross-boundary/within-word MI ratio; BPE boundary F1 | Latin true/random/every-N spaces; word-order shuffle | Voynich 0.10–0.16 (true-boundary band); F1 0.73 vs chance 0.17 | FALSIFIED (spaces are unit boundaries; CERTIFIED by WS-E with caveat units≠words) |
| WS-A-2 | Context-dependent substitution (bigram→letter) | m2_context_sub.py | key recovery; attested words≥5 | synthetic context cipher; unit-shuffle; random key | positive control only 11–18% key → underpowered; Voynich 12.6±2.5% vs null 4.5–6.2%; cross-fold key agreement 24% | UNSUPPORTED (method void) |
| WS-A-3 | Transposition + verbose substitution | m3_transposition.py | fit score; attested | correct/wrong T⁻¹ on synthetic | reversal ≈ identity; columnar → wrong-T signature | UNSUPPORTED / FALSIFIED (columnar) |
| WS-A-4 | Fixed-rule null glyphs | m4_nulls.py, m4b_deterministic.py | held-out bits/word gain; h2 | Latin with stochastic nulls (detected); placebo deletions | no (unit,position) rule with positive gain; h2 stays 1.96–2.23 | UNSUPPORTED |
| WS-B-acq | Obtain Old Occitan & MHG | clean_acquired.py | — | — | archive.org OCR texts obtained | DONE |
| WS-B-1 | Abjad / vowel omission | m1_abjad.py, m1b, m1c | fingerprint; skeleton attestation; key stability | 9 langs × 4 variants; grille & slot-grammar nulls; random key | encoder never matches all 3 stats; decoder signal equalled by grille (80%) and slot generator (85%); key agreement 37% = grille 38% | FALSIFIED (encoder) / UNSUPPORTED (decoder) |
| WS-B-2 | Exact medieval abbreviation rules | m2_abbrev.py | h2, sd, slot coverage | 128 rule subsets × 2 corpora | min h2 3.34; compressing rules raise h2 | FALSIFIED |
| WS-B-3 | Syllabary | m3_syllabic.py | unit stats; units→syllable search | relabelled Italian/Latin syllables | positive control 5.6%/0% → void; units letter-like (alternation 0.75) | UNSUPPORTED (no power) |
| WS-B-4 | Positional allographs | m4_allographs.py, m4b, m4c | held-out bits vs placebo merges; h2 ceiling | 100 placebo reps; planted-allograph Latin | merges cost ≥ placebo; 10 greedy merges lift h2 only to 2.5–2.8 | UNSUPPORTED |
| WS-C-1 | Word n-gram KN (M1) | run_nonling.py | bits/word 5-fold | — | 12.73±0.33 | baseline |
| WS-C-2 | Char n-gram (M2) ± context | run_nonling.py, run_hybrid.py | bits/word; PPC | — | 12.00 plain → 11.70 conditioned; reproduces y→q and line-final m | SUPPORTED-STRUCTURAL (WS-E: PPC thresholds post hoc; models condition on the defining variables) |
| WS-C-3 | Slot grammar (M3) | run_nonling.py | bits/word; PPC | — | 12.71 conditioned; reproduces both effects | SUPPORTED-STRUCTURAL |
| WS-C-4 | Probabilistic self-citation (M4) | run_nonling.py | bits/word; EM weights | — | 11.96; EM gives 96% weight to fresh words, <0.1% to copies | UNSUPPORTED (copying not favoured) |
| WS-C-5 | Verbose cipher of Latin/Italian/Old French (M5/M6) | run_cipher.py | bits/word; Δ vs scrambled lexicon | positive control (15–18/18 letters); scrambled lexicon | 12.81 vs scrambled 12.83 (Δ −0.02) | FALSIFIED as information source (WS-E: 0.8-bit gap to M2 is a fixed-prior artefact; true statement: lexicon contributes ≈0 bits) |
| WS-D-img | Acquire Yale images | ws_d_zodiac/scripts | — | — | 6 pages obtained; figure counts match transcription | DONE |
| WS-D-1 | Labels = degree numbers | scripts | same-ordinal Dice; progression | 2000 within-ring perms; planted control p=0.002 | z=−0.88, p=0.81; repeated labels within ring | UNSUPPORTED |
| WS-D-2 | Labels generated from neighbours | scripts | adjacent Dice | perms | p=0.067 / 0.14 | UNSUPPORTED (weak trend) |
| WS-D-3 | Ring = decan | scripts | JS by ring | perms | p=0.63 / 0.79 | UNSUPPORTED |
| WS-D-4 | Labels = unique star names outside prose grammar | scripts | uniqueness; prose-vocab overlap | length-matched prose | 87% unique = expectation (p=0.68); overlap deficit shared by herbal/pharma labels | UNSUPPORTED |
| WS-D-5 | Label/prose register difference | scripts | first-glyph JS; q-rate | group permutation | 0.139 vs 0.026±0.009, p=0.0005 | SUPPORTED-STRUCTURAL (CERTIFIED) |
| WS-E | Adversarial audit | ws_e_adversarial/ | replication; leakage; break attempts | — | no blind leakage; M5 gap downgraded; R1 "held-out" framing rejected | see ADVERSARIAL_REPORT.md |
| B-P1 | M2cond < M5lat − 0.8 on blind | BLIND_EVALUATION/run_blind.py | bits/word | pre-registered | 11.009 vs 12.114 | PASS (but see WS-E: margin is a fixed-prior artefact) |
| B-P2 | M5lat ≈ M5scrambled | run_blind.py | Δ bits | pre-registered | −0.024 | PASS |
| B-P3 | y→q generalizes | run_blind.py | q-rate after y − other | pre-registered ≥0.20 | 0.639 − 0.212 = 0.43 | PASS |
| B-P4 | line-final m generalizes | run_blind.py | m/(m+iin) end vs within | ≥0.40 / ≤0.15 | 0.413 / 0.102 | PASS |
| B-P5 | leaf-72 label register | run_blind.py | q-rate ≤3%; ot/ok/op/of ≥55%; unique ≥80% | pre-registered | 0.0% / **48.6%** / 90.3% | **FAIL** (ot/ok/op/of threshold) |
| B-P6 | M2cond samples reproduce effects, M5lat do not | run_blind.py | PPC on blind layout | pre-registered | M2: 0.59/0.28 & 0.53/0.13; M5: 0.46/0.38 & 0.17/0.10 | PASS |