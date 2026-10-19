# What we have done so far: a summary (E001–E025 and Stage B development)

Updated 2026-10-19. This document is for readers new to the project. Each experiment's own report, pre-registration
and result files hold the full detail, and `experiments/LEDGER.csv` holds every logged number.

> **Bottom line: no decipherment.** No reading of any Voynich word is proposed here. We have built and validated
> tools, ruled out several families of explanation, and narrowed the space down to a few hypotheses that can be
> tested. Every negative result is published alongside the positive ones.

---

## 1. The question and how we approach it

**What we want:** to decipher the Voynich Manuscript (Beinecke MS 408) legitimately. That means a reading that any
sceptic can reproduce, that covers the whole text and not hand-picked words, and that predicts things it was never
fitted to.

**Three doors** (`reports/METHODOLOGY.md`):

| Door | Meaning | Can it be settled with certainty? |
|---|---|---|
| 1 | A known language hidden by a system (cipher, invented alphabet, shorthand, code) | Yes. By Shannon's unicity argument, 28,000 words is far more text than a correct key needs to stand out |
| 2 | A language we have no text for | Only with anchors (names, pictures, a bilingual), as with Linear B |
| 3 | No language (meaningful-looking gibberish) | Never with certainty, only with probability. But a *consistent* gibberish is hard to write, and that consistency is something we can measure |

**Rules of evidence**, which every test follows:
1. **Pre-registration.** The question, data, procedure and decision rule are written before the run. The file is
   then locked read-only and its sha256 recorded.
2. **Locked pages.** 15 LOCKED_TEST leaves are held back for one final confirmation. They were scored once, in
   E002, by frozen structure models only; no decoding attack has ever seen them.
3. **Known answers first.** An attack must crack synthetic texts of its own hypothesis class, with every hidden
   part kept hidden, before it is ever pointed at Voynich.
4. **Controls.** Meaningless look-alike texts are attacked the same way, and zero false claims are allowed.
5. **Two independent success signals:** independent restarts must agree, and the decoded text must contain real
   long words.
6. Readings must cover the whole text.
7. Confirmation must be independent.
8. Every result is published, including every null.
9. **Positive controls for meaning tests.** A test that is meant to detect meaning must first be shown to detect it
   in a real text of the same kind.

---

## 2. The work, phase by phase

### Phase 0: data and structure (E001–E002)
- **E001.** We parsed the ZL3b IVTFF transliteration with full provenance: 39,020 tokens, of which 35,069 are prose.
  The split is by physical leaf, giving 85 DEV leaves and 15 LOCKED_TEST leaves, and the effects known from the
  literature reproduce.
- **E002.** Voynich-native structure models, trained on DEV, were scored once on the locked leaves:

  | Model | bits/glyph | bits/word |
  |---|---|---|
  | Unigram | 3.97 | — |
  | Kneser-Ney 4-gram | **1.92** | **11.5** |

  Glyphs are far more predictable than letters in ordinary alphabets. Several checks failed: the models
  under-produce label-initial *ot/ok* words, and the line-position effects come out wrong.
  (`reports/STRUCTURAL_FINDINGS.md`)

### Phase 1: can a machine learn to decipher at all? (E003–E009)
We built a known-answer benchmark: 36 languages × 13 encoding families × decoys (`DATASET_CARD.md`, `eval/PROTOCOL_v1.md`).

- **E003, classical solver.** It solves simple ciphers but none reliably enough: no family reaches 90% letter
  accuracy. It fails on unseen encodings, and order-2 Markov decoys fooled it 5 times in 80.
- **E004, LLM hypothesis agent** (Claude proposing mechanisms). It was no better than exhaustive search over the
  same operations.
- **E005, self-null abstention.** The solver now abstains unless it beats re-solves of scrambled text. The decoy
  false-discovery rate fell from 6.3% to 1.3%, so Gate 3 passes.
- **E006, fingerprint ranking.** Voynich is outside the 95% range of *every* known-answer class tested.
- **E007, two mechanisms fitted to Voynich's fingerprint.** Neither reaches the noise floor (0.99):

  | Mechanism | Distance |
  |---|---|
  | Meaningless slot grammar | **1.15** |
  | Verbose cipher of real language | 3.31 |

  So statistics alone favour neither meaning nor nonsense.
- **E008, NeuroDecipher** (Luo et al. 2019). Ugaritic reproduces at 73.3%; Linear B does not reproduce from the
  released code.
- **E009, neural decipherer** (Qwen2.5-0.5B + LoRA, SFT and GRPO). It solves nothing and learns little beyond
  frequency analysis: a negative result. (`reports/NEURAL_DECIPHERER.md`)

### Phase 2: anchors, twins and units (E010–E015)
- **E010/E010B–D, anchors.**
  - *What we tested:* the zodiac month names, the plant identifications, and same-month page pairs.
  - *Result:* the real anchor set is too weak to identify a key. A pre-registered month-name test was negative,
    but it only had power against one-glyph-per-letter spellings.
  - *Also shown:* a worked example of how searching through choices "manufactures" a significant-looking anchor.
    (`reports/ANCHORS.md`)
- **E011, Voynich twins.**
  - *What we tested:* five mechanism families fitted to Voynich's statistical fingerprint, with meaningless
    generators as decoys (Rugg's grille; Timm & Schinner's self-citation).
  - *Result:* no family reached Voynich's own variation. (`reports/VOYNICH_TWINS.md`)
- **E012, unit inventories.** No choice of glyph units makes Voynich look like an ordinary alphabet or syllabary.
  (`reports/UNIT_INVENTORIES.md`)
- **E013–E014.** Greshko's published Naibbe cipher, plus two small, decodable additions, becomes a **full twin** on
  all 16 + 6 features, for Latin, Italian, French and German plaintext. The additions are context-dependent
  spelling ("sandhi") and about 2% nulls. (`reports/EDGE_TWINS.md`, `reports/REP_TWINS.md`)
- **E015.** The twin needs real *words* underneath, but not real *sentences*: word-shuffled text fits just as well.
  (`reports/SHUFFLED_CONTROLS.md`)

### Phase 3: the first validated attack (E016–E018)
- **E016.** The first known-answer test of an attack on this cipher class **failed**: it cracked 3 of 8 texts, and
  one meaningless control looked better than every success.
- **E017.** We switched to delta scoring (about 10× faster), used 128 short restarts, and adopted a two-signal claim
  rule (restart agreement ≥ 0.95 and long-word coverage ≥ 0.08). The attack then **passed**:

  | Check | Result |
  |---|---|
  | Full-size texts cracked | 8/8 |
  | False claims on 32 control attacks | 0 |
  | Language identified | 8/8 |
  | Quarter-size texts cracked | 8/8 |

  (`reports/PORTFOLIO_KNOWN_ANSWER.md`)
- **E018.** The validated attack on Voynich returned **NO CLAIM** in all 12 attacks (DEV, Currier A and Currier B,
  each against Latin, Italian, French and German):

  | | Agreement | Long-word coverage |
  |---|---|---|
  | Voynich attacks | 0.50–0.74 | ≤ 0.009 |
  | Real cracks | ≥ 0.99 | ≥ 0.14 |

  Voynich is not Naibbe-tables × these four languages. The published tables also leave 20% of Voynich words
  unparsed. (`reports/VOYNICH_ATTACK.md`)

### Phase 4: Stage A, cheap tests that shrink the space (E019–E025)

| Test | Question | Result |
|---|---|---|
| E019 (A1) | What size of unit does a Voynich word carry? (topic clustering) | Word-sized. A fixed-key letter cipher, Rugg and self-citation are out (the first is out for a *fixed* key only, see E020) |
| E020 (A1b) | Changing keys and compound words | A drifting-key cipher fits the word level but not glyph pairs; compound words come closest |
| E021 (A1c) | Do common words persist like grammar words? | Yes. Consistent: word, compound, and drifting cipher. Out: fixed-key cipher, Rugg, self-citation, syllables |
| E022 (A2b) | Do look-alike plants share words? (blind image coding) | Nothing found (r = 0.015)… |
| E023 | …but could the test find it in a real herbal? | No: Culpeper gives r ≈ 0 too. The test has no power, so this line was dropped and rule 9 added |
| E024 (A3) | Does any glyph grouping look like an alphabet? | No. Conditional entropy is 2.10–2.48, against ≥ 2.79 for all 34 languages |
| E025 (A4) | Are line effects a by-product of the system? | No. Voynich's line-start/line-end effects (V = 0.39/0.33) are reproduced by no tested system (≤ 0.08; ≤ 0.23 even with explicit line rules), so the line is a functional unit |

**The picture after Stage A.** Voynich behaves like word-sized units (whole words, or stem + ending) whose common
words persist the way grammar words do. Within words the glyphs are far more predictable than any alphabet's
letters, and lines have their own start and end conventions. This points to a **word-level system** (a codebook,
nomenclator, or compound stem + ending notation) under strong line conventions, rather than a letter-by-letter
cipher or a simple invented alphabet. Meaning versus human gibberish is still open. (`reports/STATUS_2026-10-18.md`)

### Phase 5: Stage B development, a word-level attack (in progress)
These are development probes on synthetic Latin with known answers. Voynich has not been touched.
(`reports/STAGE_B_DEV.md`, `experiments/dev/`)

**Word-for-word code.**
- The scoring yardstick only became sound with a large open corpus: the CLTK Latin Library, 13M words, with any
  overlap with test texts removed.
- With it the true key wins (−4.73 vs ≤ −5.52), so the problem is now the search.
- Best search so far: 31–40% of frequent-word tokens.

**Compound code (stem + ending)**, which follows the E020/E021 hints:

| Stage | Result |
|---|---|
| Endings decoded on their own, from frequency, neighbouring endings, and which endings share a stem (Kober's Linear B insight) | **98.8%** of ending tokens |
| Then stems | 58% of stem tokens |
| Whole words exactly right | 53% of all tokens |

So far the split into stem and ending is given to the attack; learning it from the text is the next step.

---

## 3. What is ruled out, what is open

| Status | Hypothesis |
|---|---|
| **Out** (for the classes tested) | Naibbe tables × la/it/fr/de (E018); fixed-key letter cipher (E019/E021); Rugg grille, self-citation (E011, E019, E021); syllabary (E021); simple alphabet over any tested glyph grouping (E012, E024) |
| **Favoured** | Word-level codebook / nomenclator; compound stem + ending notation; drifting-key cipher at word level; all with line conventions |
| **Open** | Which language; meaning versus consistent human gibberish (no powered meaning test yet) |

## 4. Next steps
1. Stage B:
   - learn the stem/ending split from the cipher itself;
   - add restarts with the agreement and long-word checks;
   - add a line model;
   - then a **pre-registered known-answer test with meaningless controls**, and only after that, Voynich DEV.
2. More period corpora: medieval Latin, Old Italian and other vernaculars.
3. A meaning test with built-in power: label consistency, checked first on a real labelled manuscript.
4. The same method for the Indus script, which is a Door-2 problem: structure plus anchors.
