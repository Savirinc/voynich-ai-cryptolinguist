# Voynich MS 408 — Adversarial Decipherment: Final Report
**Date:** 2026-10-15 · **Repository:** `voynich-lab/` (code, logs, results, ledger) · **Outcome: documented failure analysis (Deliverable 2).** No decipherment was obtained, and the published 87.8% claim was falsified as evidence of decipherment.

## 0. Bottom line
1. **The Schechter "87.8% decoded" claim reproduces (89.2% with the current 4,063-entry glossary) but is a dictionary-size artefact.** A dictionary of the 4,063 most frequent Voynich word types *with any meanings at all* covers 89.4% of tokens. Coverage is mathematically invariant under shuffling all meanings. The cipher "rules" are two: look the word up; if absent, delete gallows glyphs and look it up again. Frozen rules decode **5.0%** of word types unseen on held-out folios. It is a lookup table, not a cipher.
2. **The decoded text is not Latin or Occitan.** 583 of 947 target words (62%) are attested in neither a 13.3M-word Latin corpus nor an Old French corpus; 25 of the 36 advertised "NOCERE" forms are invented (NOCITIS, NOCS, NOCAN, NOCUM, NOCAT, NOCAR…). Shuffling decoded words *within each line* leaves the Latin-bigram attestation unchanged (11.9% → 12.0%, z = −0.47; real Latin: 48.7%): **the output has no syntax**.
3. **Independent semantic tests fail.** On the 12 zodiac pages, 361 nymph/star labels decode to "you (pl.) make", "to", "praises", "love", "and" — zero sign names on 10/12 pages; ARIETE lands 15× in the herbal section and once in the zodiac; 1 of 93 pharmacy-jar labels is an ingredient; the headline plant identifications are each a single hapax assigned to one word on the folio chosen to match the drawing.
4. **Every classical cipher family into every tested language is falsified or unsupported.** Monoalphabetic, homophonic and polyalphabetic substitution are excluded by entropy/IoC invariants (Voynich h2 = 2.0–2.5 bits vs 3.1–3.4 for Latin, Old French, Italian, Middle English, Occitan, German). Scribal abbreviation moves entropy the wrong way. A verbose-cipher search engine that recovers 85–92% of a genuine random verbose cipher finds no mapping for Voynich A or B into any of the seven languages: 0.2–7% real words (≥5 letters) vs 25–35% achievable on a real noisy cipher.
5. **What survives:** (a) a verbose/positional encoding into a language or unit inventory not tested here; (b) a syllabic or code-like system with extreme positional constraints; (c) structured non-linguistic generation. Each is OPEN with specified next evidence (ledger).

## 1. Phase 1 — Reproduction and audit of scott-schechter/voynich-decoded (commit 71f2f3c)
- `node decode.js` → 33,785 / 37,886 tokens = 89.2% (README: 87.8% with 3,648 entries — the glossary has since grown; the repo's own `coverage-push.js` is a tool for adding entries to raise the number).
- Mechanism: direct lookup (85.5%) + gallows-stripped lookup (3.6%). No other transformation exists in the code.
- Glossary anatomy: 4,063 keys → **947** distinct targets (4.3 Voynich words per "Latin" word); **1784** keys are hapax legomena (occur once; unverifiable), 66 keys never occur. Top targets by token share: OLEUM 2.7%, FUIT 2.1%, DEUS 2.0%, DES 2.0%, DICIT 1.9%, HEUS 1.8%, AMARA 1.8%; "you (pl.) harm" (NOCETIS+NOCITIS+NOCIS+NOCS) ≈ 4.6% of all tokens. In the "biological" section 19.4% of decoded tokens are forms of *to harm*.
- Zipf baseline: top-K frequency dictionary coverage K=1000: 75.2%; K=2000: 82.6%; K=4063: 89.4%; K=6000: 94.5%. The repo's "2.1% random baseline, 42× ratio" compares against the wrong null.
- "Reverse encoding test" (doc 13): source words were taken from the decoder's own output and encoded through the glossary's reverse map; the round trip is tautological.

## 2. Phase 2 — Adversarial validation (scripts: `phase2_adversarial.py`, `phase2_stratified_null.py`)
| Test | Result |
|---|---|
| Coverage with all meanings randomly reassigned | 89.18% (= true 89.18%) |
| Held-out folios (seed 42, 50/50): unseen-type tokens decoded by frozen rules | 166/3308 = 5.0% |
| Targets attested in Latin corpus / Old French / neither | 357 / 81 / **583** of 947 |
| Latin-bigram attestation of adjacent decoded pairs | true 0.119; meanings shuffled (unstratified, 200×) 0.073±0.014; frequency-stratified shuffle 0.103±0.008 (p≈0.045); **word order shuffled within line 0.120±0.002**; genuine medieval Latin 0.487 |
| Section semantics | harm-verbs: Biological 19.4%, Stars 12.5%, Zodiac 0.9%; plant names in Herbal 1.8% (vs 2.7% Pharma, 3.4% Cosmological) — no section-appropriate vocabulary |

## 3. Phase 3 — Competing engines (scripts: `phase3_fingerprint.py`, `phase3_structure.py`, `phase3_cipher_families.py`, `phase3_cipher_search.py`)
### 3.1 Fingerprint (paragraph text only; A = Currier A, B = Currier B)
| text | h1 | h2 | h3 | IoC | wordlen μ/σ | Zipf | TTR20k | adj. ed-1 | line-first Δlen |
|---|---|---|---|---|---|---|---|---|---|
| voynich_A_evachars | 3.83 | **2.14** | 1.87 | 1.63 | 4.9/1.7 | -0.92 | nan | 0.046 | +0.53 |
| voynich_B_evachars | 3.86 | **2.00** | 1.73 | 1.53 | 5.2/1.7 | -0.97 | 0.22 | 0.039 | +0.43 |
| voynich_B_evaunits | 4.04 | **2.36** | 2.12 | 2.35 | 3.9/1.4 | -0.97 | 0.22 | 0.049 | +0.38 |
| latin_medieval | 4.03 | **3.36** | 2.83 | 1.70 | 5.7/2.7 | -0.91 | 0.37 | 0.004 | -1.09 |
| latin_technical | 4.00 | **3.34** | 2.80 | 1.74 | 5.9/2.7 | -0.87 | 0.38 | 0.004 | -1.96 |
| oldfrench | 4.03 | **3.16** | 2.66 | 2.01 | 4.0/2.2 | -1.02 | 0.21 | 0.024 | -0.32 |
| italian_dante | 4.01 | **3.11** | 2.65 | 1.74 | 4.0/2.2 | -1.02 | 0.23 | 0.021 | -0.10 |
| middle_english | 4.15 | **3.24** | 2.63 | 1.73 | 4.0/2.0 | -1.03 | 0.18 | 0.013 | -0.31 |
| occitan_modern | 3.97 | **3.26** | 2.67 | 1.99 | 4.8/3.1 | -0.95 | nan | 0.026 | -0.50 |
| german_modern | 4.11 | **3.32** | 2.59 | 1.90 | 6.7/4.2 | -0.91 | nan | 0.004 | -0.56 |
| CTRL_rugg_grille | 4.06 | **2.52** | 2.24 | 1.57 | 4.6/1.1 | -0.26 | 0.20 | 0.231 | -0.01 |
| CTRL_slot_grammar | 4.21 | **2.80** | 2.51 | 1.46 | 4.2/1.2 | -0.37 | 0.40 | 0.006 | +0.03 |
| CTRL_latin_abbrev | 4.15 | **3.40** | 2.89 | 1.76 | 4.7/2.1 | -0.86 | 0.32 | 0.005 | -0.60 |
| CTRL_random_chars | 4.01 | **3.88** | 3.79 | 1.61 | 4.4/1.5 | -0.58 | 0.85 | 0.003 | -0.04 |

Observations: Voynich h2 is 0.6–1.3 bits below every language at every granularity (raw EVA, merged units, minim-counts 2.38/2.17); word-length σ is 1.7 vs ≥2.0; line-initial words are *longer* than mid-line (+0.4) while in every language they are shorter or equal; glyphs are far more position-bound (first/last-vs-mid JSD 0.29/0.72 bits vs ≤0.20 in languages).

### 3.2 Structure
- A fixed 4-slot word grammar (prefix·mid·mid·suffix) parses **86% / 87%** of A/B tokens (62%/58% of types) vs 10–35% of tokens and 1–5% of types for the seven languages. Voynichese words are positionally rigid in a way no plaintext is.
- Currier A vs B: word-distribution JSD 0.476 bits ≈ medieval-vs-technical Latin (0.445), ≪ Old French vs Italian (0.756); glyph-level JSD 0.026. One system, two registers.

### 3.3 Cipher families — invariant falsification (full table: `results/phase3/cipher_families.json`)
Monoalphabetic ✗ · Homophonic ✗ · Polyalphabetic ✗ · Scribal abbreviation ✗ (simulated: h2 3.40) · Plain natural language (7 tested) ✗ · Verbose cipher: consistent with invariants, unsupported by search (§3.4) · Syllabary: weakened · Non-linguistic generation: open.

### 3.4 Verbose/positional cipher search (iterated local search over unit→letter maps; trigram LM + unigram-KL; 12 rounds × 3 restarts; 2,500-word samples; seeds fixed)
| language | real text | positive control (random verbose cipher of held-out text, recovered) | unit-map acc. | shuffled Voynich | Voynich A | Voynich B | words≥5 attested: real / perfect noisy decode / **A** / **B** |
|---|---|---|---|---|---|---|---|
| latin_medieval | -2.96 | -3.70 | 85% | -4.78 | -3.77 | -3.60 | 51% / 25% / **6.1%** / **3.2%** |
| latin_technical | -2.83 | -3.61 | 85% | -4.79 | -3.86 | -3.74 | 52% / 24% / **0.8%** / **6.8%** |
| oldfrench | -3.31 | -3.66 | 85% | -4.87 | -3.65 | -3.83 | 51% / 24% / **4.7%** / **2.1%** |
| italian_dante | -2.70 | -3.34 | 92% | -5.12 | -3.86 | -3.81 | 72% / 35% / **4.9%** / **7.1%** |
| middle_english | -2.66 | -3.37 | 85% | -5.16 | -3.91 | -3.95 | 75% / 32% / **0.2%** / **4.2%** |
| occitan_modern | -3.07 | -3.57 | 92% | -4.70 | -3.67 | -3.65 | 39% / 17% / **0.2%** / **0.6%** |
| german_modern | -2.73 | -3.49 | 92% | -4.83 | -3.71 | -3.84 | 41% / 17% / **0.6%** / **0.2%** |

The engine demonstrably works (readable recovered Latin: *"vero illam vocamus in sua personam fingimus pro exprimendis affectibus aetatis"*). Applied to Voynich it converges to language-shaped nonsense (B→Latin: *"tam ius dem turgio inta taem ins em tem dem sens…"*; B→Italian: *"nel sai con narede stne neon sti ol nol col…"*). Whatever Voynichese is, it is not a fixed unit-to-letter encoding of these seven languages at EVA-unit granularity.

## 4. Phase 4 — Semantic verification (script: `phase4_semantic.py`)
- Zodiac nymph labels: 367 tokens, 237 decoded, only 113 distinct outputs for 361 nymphs; top outputs FACITIS, AD, LAUDAT, FACIS, AM, ET. Sign-name hits: Pisces 0, Aries 0+1 (TELI = Hebrew "dragon"), Taurus 0, Gemini 0, Cancer 0, Leo 0, Virgo 0, Libra 2 (TELI), Scorpio 0, Sagittarius 0.
- Where the decoder's own zodiac words fall: ARIETE {'Herbal': 15, 'Unknown': 5, 'Zodiac/ZODIACPAGE': 1, 'Biological': 4, 'Stars/Recipes': 7}; LEO {'Herbal': 4, 'Cosmological': 1, 'Unknown/ZODIACPAGE': 2, 'Zodiac/ZODIACPAGE': 1, 'Unknown': 2, 'Pharmaceutical': 1, 'Stars/Recipes': 5}.
- Pharmacy jar labels: 146 labels, 93 decoded, **1** ingredient name.
- Herbal plant names: BASILICUM, MANDRAGORA, VERBENA, ARUM = 1 token each (hapax on f1v, f4v, f11v, f25v); SENECIO spread over 31 folios, ALOE over 26.

## 5. Phase 5 — Scale, provenance, negative results
- Compute: 2 vCPU, no GPU; two jobs run in parallel throughout. Search budgets are CLI arguments; everything is seeded.
- Corpora gaps (honestly noted): Old Occitan and Middle High German were not obtainable from the allowed sources; modern Occitan/German Wikipedia text (60–90k chars) was used as fingerprint proxies and Old French as the closest Gallo-Romance proxy for Occitan. Hebrew/Arabic in transliteration, Czech, Hungarian, Greek were not tested.
- My non-linguistic generators (grille, slot grammar, self-citation) reproduce entropy and word-length but **not** the Zipf slope (−0.3 vs −0.9); this is a limitation of my reimplementation, recorded as a negative result, not a falsification of Timm–Schinner.
- All failed attempts, including the two abandoned optimizer variants (simulated annealing with null moves — exploitable; SA without frequency init — non-convergent), are in `logs/` and the git history.

## 6. What would change the conclusion
See `ledger/HYPOTHESIS_LEDGER.md` and the pre-registered protocol `ledger/PROTOCOL.md`. Any future claim must (i) beat a frequency-matched dummy dictionary, (ii) decode unseen word types with frozen rules, (iii) lose its linguistic signal under within-line word-order shuffling, (iv) use ≥90% corpus-attested forms, and (v) predict zodiac/pharmacy label content declared in advance.