# CLAUDE.md — Voynich AI Cryptolinguist

Read this first in every session. It carries the full working context; details live in `reports/`.

## 1. What this is
- **Goal:** decipher the Voynich manuscript (Beinecke MS 408) **legitimately and with certainty**: reproducible,
  whole-text, predictive, never cherry-picked.
- **Owner:** Arham Partap Jain / Savir Platforms Private Limited.
- **Licence:** MIT. Public repo: github.com/Savirinc/voynich-ai-cryptolinguist (HTTPS remote; `git push` works from
  here).
- **Indus is separate.** Arham runs Indus himself (github.com/Savirinc/indus-script). **Never steer Voynich work
  towards Indus.**

## 2. How Arham works (follow exactly)
- **Explain everything in plain language.** He is not a statistician. Define terms (glyph, EVA, Currier A/B and so
  on) when they first matter, and use short tables.
- **After every test, first explain it as to a bright 10-year-old:** what we did, what we found, what it means, with an
  everyday analogy, before any numbers or ledger talk. He must never lose the thread between tests.
- **He approves each test with "ok" or "yes".** Propose one next test at a time, with a clear recommendation, and wait
  for approval before pre-registering it.
- **From 2026-10-27 Arham dictates the order of work.** Carry out the step he names; after a result, report it and ask
  what he wants next instead of pushing a recommended test.
- **He wants the truth, not a story.** Report failures, VOID results and corrections plainly, and correct earlier
  claims when new evidence contradicts them.
- **Symmetric Bayes.** "Don't rule out gibberish": the meaningless hypothesis (M) must face tests it can win, as
  strongly as L has. Absence of evidence counts (the "dog that didn't bark").

## 3. Standing rules (non-negotiable)
1. **Pre-register every test** in `reports/E0NN_PREREG.md`:
   - question, data, procedure, decision table and Bayes factor for each outcome;
   - what was seen beforehand.

   Then `chmod 444` both the prereg and the script, and put both sha256 values in the commit message *before*
   running.
2. **Fixed-bug amendments** go in a locked `E0NN_AMENDMENT.md` plus a `_v2` script, written before the rerun. Never
   edit locked files.
3. **LOCKED_TEST leaves (15; `vcl.corpus.splits.locked_test_leaves`) are never touched.** That covers their text and
   also their **images**.
   - The pharma fold-out canvases that include **f102** must not be downloaded.
   - When cropping shared canvases, stay well inside the DEV page.
   - Two slips so far are recorded in LEDGER (an f102r image displayed once; two f102 canvases downloaded and deleted
     unviewed).
4. **Run one job at a time** with `caffeinate -ims`. Commit and push results with
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Clear background jobs after reading them.
5. **Occam's rule** (`reports/OCCAM.md`): test the simplest hypothesis first; add a layer only when a measured fact
   forces it.
6. **Check earlier reports first:** `reports/SUMMARY.md` (E001–E029a), `reports/LEDGER.md`, the reports E030–E073
   (`reports/CLEANUP_ROUND.md` is E059, `reports/INGREDIENT_LINK.md` E060, `reports/STEM_STREAM.md` E061,
   `reports/SCRIBE_TABLES.md` E062, `reports/WIDE_ATTACK.md` E063, `reports/EARLY_AUDIT.md` E064,
   `reports/SYLLABLE_GONOGO.md` E065, `reports/WORD_INDIVIDUALITY_V3.md` E066, `reports/GIBBERISH_VOCABULARY.md` E067, `reports/GIBBERISH_BATTERY.md` E068, `reports/WORD_PARTNERS.md` E069, `reports/CONTENT_PARTNERS.md` E070, `reports/LABEL_STEP0.md` step 0, `reports/LABEL_TRUNCATION.md` E071, `reports/FRONT_PIECES.md` E072, `reports/ZODIAC_ATTRIBUTES.md` E073), and `reports/FORUM_SYNTHESIS.md` (what voynich.ninja already knows).
7. **Known answers first:** every attack must crack synthetic texts of its own class and make **zero false claims**
   on gibberish and wrong-language controls before it touches Voynich.
8. **Seed check:** any pass or fail within about 0.5 sd gets a seed-replicate check (≥ 8 of 10 seeds) before it is
   scored (lesson of E035/E035b).
9. **No model-hunting:** declare in advance how many variants a family gets. E036 closed the spelling-variation
   family; E066 closed the per-word-repeat family (E057, E058, E066; E058's v3 was
    reopened once by the tokenizer defect).
10. **Absence rule** (`reports/ABSENCE_RULE.md`): a validated search that finds nothing multiplies the searched
    form's share by m = 0.2 (or as pre-registered).
11. **Exclusion is only by logic within a stated scope**, never by probability alone.

## 4. Environment
- **Python:** `.venv/bin/python` (3.11). Install packages with `uv pip install --python .venv/bin/python <pkg>` (there
  is no pip in the venv). Pillow is installed.
- **Java (for the Timm & Schinner generator):** `/opt/homebrew/opt/openjdk/bin/java`. Generator directory:
  `data/external/timm_schinner_generator/sct` (jar sha256 dc9b2f3c…8fef8).
- **Transcription:** ZL 3b IVTFF, parsed by `vcl.corpus.ivtff.parse`.
  - Each token has: `folio, leaf, line_no, mode` (prose/label/circle/radial), `currier, hand, quire, illustration`
    (H herbal, P pharma, B bathing, S stars, Z zodiac, A astro, C cosmo, T text), `eva, is_clean, para_start`.
  - `e011_twin_search.voynich_lines()` gives the DEV lines (28,841 tokens).
- **Local data, all gitignored under `data/external/`:**

  | Directory | Contents |
  |---|---|
  | `bibles/<id>/txt/*_read.txt` | eBible texts: about 60 translations (Hebrew hboWLC, Turkish turytc, Latin latVUC, Czech ces1613, Tamil tam2017, Assamese asmfb, Malayalam mal, Indonesian indayt, Vietnamese vie1934, cmn-cu89s…) |
  | `latin_library_e043/` | hymns, Prudentius, Apicius, Cato, Varro, Columella, Vergil, Ovid, Caesar |
  | `latin_library_pickles/` | older CLTK Latin Library pickles |
  | `pg_herbal/pg49513.txt` | Culpeper's herbal |
  | `wals_v2020.4/` | WALS CLDF |
  | `gaskell_bowern_repo/`, `gaskell_bowern_unzipped/` | human gibberish (38 writers) and their 72 meaningful texts, including abbreviated Latin |
  | `beinecke_images/` | IIIF manifest, `img/` (herbal and pharma pages at 1400 px), `hi/` (pharma canvases at high resolution), `map_*.json` (label→drawing maps), `e055_pairs/` |
  | `voynich_ninja_raw/` | raw forum extracts |
  | `misc/` | eBible catalogue, word-frequency JSON |

- **Tracked data:**
  - `reports/data/voynich_word_frequencies_DEV.csv` (all 7,060 DEV word types);
  - `experiments/results/e055_maps/` (label maps);
  - `reports/literature/` (four forum reports);
  - `reports/artifacts/` (HTML sources of the published pages).

## 5. Where things stand (2026-10-27, after E073; M/L/C unchanged since E068)
**Ledger** (`reports/LEDGER.md`): **M 0.0739, L 0.8938, C 0.0281, O 0.0041** (after E068).
- **M** = meaningless; **L** = a real language in its own script; **C** = cipher or code; **O** = other.
- **Honest range:** L about 0.17–0.89, M about 0.07–0.69, C about 0.03–0.12. **From the range edges M leads (0.69 vs
  0.17)**; at the point values L leads (0.89 vs 0.07). A two-horse race; treat M and L symmetrically. E066's × 3 is pre-registered; its empirical ratio is 1.4 (most real languages
  are also family-level), which would give M 0.035: the M-versus-L ranking depends on the starting point. E064 withdrew E031 (L × 3); E030 and E032 stand.
- **Tokenizer defect (E064):** the old Bible loaders split Indic-script words at vowel signs. Use E064's `tok` (letters,
  marks, apostrophes) for any new language work; E051's Tamil/Assamese matches were fragments.

**E068 (scored, M × 1/3):** the same gibberish pages are language-like, not Voynich-like, on word-length spread, letter
predictability, ending concentration and back-to-back repeats; Voynich-like only on near-copies (NR 1.31). The generator
has the opposite profile (shapes and endings, no vocabulary). No testable meaningless process has both halves.

**E067 (scored, M × 3):** 36 humans writing gibberish make Voynich's vocabulary richness in 150-token windows (115
distinct words, 67% one-offs vs Voynich 112 / 62%); Bibles 95 / 47%, generator 94 / 46%. Caveat: 14 of 60 languages
(Hebrew, Tamil, Arabic, Turkish…) are as rich; only 150 tokens. Human gibberish is untested on near-copies, endings,
h2 and word length (AS was 0.66, E045).

**E066 (scored, M × 3):** Voynich's common words repeat back to back as their shape-families predict (z −1.2), like the
generator; Tagalog, Indonesian, Oromo and Lingala give words individual habits (z +4 to +14). Per-word-repeat family
closed (E057, E058, E066).

**Four unscored cautions that lean towards M:**
- **E070:** content-like words have no partnerships that persist across the book (0.004; all 60 languages ≥ 0.018);
  the rule's A-only safeguard failed by a hair (0.009 vs 0.008), so no factor;
- **C21 (reinstated by E064):** among about 120 meaningful texts, only Indonesian reaches Voynich's back-to-back repeat
  level; human gibberish (0.66) and the copy generator (0.76–0.81) get most of the way;
- a 2026 generator (quimqu, voynich.ninja thread-6219) reproduces C9/C21;
- in E058, Voynich's words repeat as their *families* predict (z −1.1), like the generator, while Indonesian shows
  word-specific behaviour (+4.8).

**Sub-hypotheses:**
- L-sacred 0.30 / L-practical 0.45 / L-other 0.25 (shares of L; E043 gave no factor);
- SYLL-UNIT (spaces separate syllables) 0.08;
- ORDER-SCRAMBLED 0.15;
- NUMBERS (zodiac labels) 0.024.

**Forms of L** (`ABSENCE_RULE.md`; shares of L after E071, priors in brackets):
- **L-unattested 0.35 (0.20):** a lost, unrecorded or constructed language; untested and unsearchable by dictionary.
  **Leads within L.**
- **L-syll 0.21 (0.20):** syllable signs. E065 NO GO: 25 Voynich final-group classes vs 284–481 final syllables (68–154
  with codas dropped) in 9 European-region languages; each-word-one-syllable fails by 4× in vocabulary.
- **L-other 0.17 (0.10).**
- **L-alpha-known 0.15 (0.35):** letter by letter, 60 languages searched, not found (E049–E053, E063).
- **L-abbrev 0.12 (0.15):** abbreviated Latin searched, not found (E053); label words are not truncations of longer
  words (E071, validated on G&B abbreviated Pliny); always-abbreviated forms untested.

**Validated attack (E047; VOY23 class)** — Voynich A's 23 commonest signs (cleaned EVA, S3 units), homophones, 12%
spelling slips, many-to-one annealing with a 4-gram KN LM with spaces. Claim requires:
- agreement ≥ 0.95;
- lexrate ≥ a calibrated threshold;
- beating pseudo-Voynich and generator controls.

**Searched, not found:** Hebrew, Turkish, Latin, Czech, Serbian-Croatian, Slovak, Ukrainian, Romanian, Italian,
Romani (E049–E052); abbreviated Latin, technical and sacred (E053); 49 more languages on Voynich A and B (E063:
German, Dutch, English, French, Danish, Swedish, Polish, Greek, Hungarian, Yiddish, Arabic, Urdu, Uyghur, Indic,
Austronesian, African and others; all validated, 0 false claims on 588 controls). Only Arabic B beat its controls
(+0.10) while staying 0.10 under threshold: disclosed as seen beforehand for the queued abjad test.
- The Hebrew "near miss" (E049) was explained by pseudo-Voynich controls.
- Blind judges called the Hebrew decodes word salad while identifying real Hebrew (2 Kings 22) (E050).

**Measured facts** (full list in LEDGER, C1–C24):
- **Physical and dating:** vellum 1404–1438; five scribes.
- **Vocabulary:** 7,060 DEV word types, 69% hapax, 149 words make up half the text.
- **Units:** glyph-level predictability is below all alphabets, and simple-syllable-like only with glyph groups.
- **Endings:** about 21–28, combining freely with stems.
- **Line recurrence:** words recur within lines, with no avoidance of back-to-back repeats (AS ≈ 1). Of about 120
  meaningful texts, only Indonesian (doubling grammar) reaches this; Assamese 0.75 is next. (Tamil and Assamese
  "matches" in E051 were tokenizer fragments, corrected in E064.)
- **Alternations:** near-copies come through five alternations (e/ee, r/l, t/k, d±, q±).
  - e = ee at word level only (what follows ee differs from what follows e; E059); t ≈ k; r ≠ l.
  - **q- is a junction form:** it appears mainly after a word ending in -y (E059; location adds nothing).
  - d± is **not** a scribe habit (E059 withdrew E039's C18); it follows line position and the previous word's -y.
- **Sheets (bifolios):** pages on the same piece of vellum share vocabulary and glyph habits; the next page in reading
  order does not (C24, E059). "Topic clustering" (C7) is really clustering by sheet. Every page-level test must
  control for sheet.
- **Currier A/B:** the same grammar shape; B is more rigid.
- **Labels:** zodiac labels are not numbers. Labels echo the vocabulary of their neighbourhood (own page, same sheet
  and adjacent page all about +4 points over frequency-matched words), not their own page in particular; pharma labels
  show the least (E059 restated C23). Same-label pharma drawings do not look alike (E055). Repeated labels are often
  common words (dar, okaiin).
- **Word order:** weak but not scrambled (like hymns or Psalms).
- **Word partners (E069):** the 200 commonest words keep weak partnerships across the two halves of the book (STAB
  0.073): more than the copy generator (≤ 0.053), less than 56 of 60 languages; like Hebrew, Polish, Slovak,
  Azerbaijani, whose commonest words are grammatical pieces. No pair is a strong partner in both halves.
- **Content-word partners (E070):** among words ranked 51–250, 15 of about 860 partner pairs persist across the halves
  (shuffled: 13). Below every language (min 0.018 vs Voynich 0.004). **Untested alternative:** a catalogue text (herbal,
  pharmacopoeia) might also lack persistent partners; test against Culpeper and the G&B technical texts before reading
  this against L.

**Re-test queue from the forum sweep** (`FORUM_SYNTHESIS.md`): E059 settled the first three (line position, e/ee/eee
glyph contexts, bifolio session effect; all confirmed, facts corrected). Still open: C3 depends on glyph grouping.

## 6. Next steps (recommended order; propose one at a time)
**Label-class programme (agreed 2026-10-25, to run from 2026-10-26).** Descriptive facts found on 2026-10-25 (not
pre-registered, in `reports/LEDGER.md` after E070 and in the session notes): labels are a word class (o + tall letter,
66% of zodiac labels vs 18% for frequency-matched text words); each label is marker + short core (1–3 signs; 69 cores
for 135 zodiac labels) + ending; 25 labels are shared between pharma drawings and zodiac figures (chance 10); those 25
words are 4–6% of running text in every section; repeated zodiac labels do not sit at the same ring position; pharma
drawing colours cannot test colour. Five readings of the label class, each to be tested properly, one pre-registration
each, cheapest first; absence counts:
0. **Line position of o-tall-letter words** (descriptive pass first): line-initial → list markers/pointers; even →
   names/abbreviations; after particular neighbours → quantities.
1. **List words and pointers** ("item", "idem", "the same"): predicts line/entry-initial position and repetition at
   entry starts; compare with real inventories/recipe books (Apicius, Cato, Culpeper, Leechbook).
2. **Title + name** (saint, lord, god, king): predicts a small set of markers with an open set of cores, cores recurring
   across sections on the *same* referent; test core sharing against drawings (same plant part/jar; same nymph type).
3. **Abbreviated phrases** (L-abbrev): predicts cores that are prefixes of longer text words (abbreviation = truncation)
   more often than chance; compare with abbreviated Latin (Pliny abbreviated, G&B).
4. **Number + unit**: predicts digit-like small core set in fixed slots and Benford-like core frequencies; already
   weakened (69 cores, no ring position, E056).
5. **Category + identifier**: predicts different markers for plants vs figures; weakened (same ot/ok ratio).
Plus the zodiac attribute test (E073 candidate: download the 8 DEV zodiac canvases, annotate ~350 labelled nymphs for
star/colour/barrel/clothing/posture; same label → same feature beyond chance).
**Status 2026-10-26:** step 0 done (`LABEL_STEP0.md`): label words open lines half as often as matched words, no
neighbour lock → reading 1 set aside, reading 4 unhelped. Reading 3 tested (E071, `LABEL_TRUNCATION.md`): NOT
ABBREVIATION-LIKE, L-abbrev × 0.6. E072 (`FRONT_PIECES.md`): *ot/ok* is detachable (z +3.7) but the generator does it
more (z +5), no factor; *ot* and *ok* act as one piece. E073 (`ZODIAC_ATTRIBUTES.md`): VOID on the reliability check (2 of 5
features passed kappa; CLOTHED failed by the kappa paradox); unscored same-label z −0.2, lean NO LINK. All five
readings tried; none ties the label class to meaning. Zodiac canvases are in `data/external/beinecke_images/zodiac/`.

1. ~~Clean-up round~~ done (E059, `CLEANUP_ROUND.md`).
2. ~~Re-audit the early ledger factors~~ done (E064, `EARLY_AUDIT.md`). Open follow-up: a test M can *win* (the
   symmetric gap): e.g. obtain or re-implement quimqu's generator (thread-6219) and run the 13-feature battery on it.
3. **Cheap leads:**
   - ~~score the published Naibbe ciphertexts on our battery~~ (E062's single-table rows did it: 10/13 fails);
   - where near-copies come from (first occurrence vs proximity vs neither), controlling for sheet;
   - ending agreement between neighbouring words (q- after -y is now known; test the rest);
   - the zodiac shed-/ched- by sign gender;
   - p vs f (f57v ring).
4. ~~Syllable route~~ NO GO (E065, `SYLLABLE_GONOGO.md`): neither a syllabary nor one-syllable-per-word fits.
5. **Constructed-language controls** (Enochian, Lingua Ignota), and an Arabic abjad attack (words of 4+ glyphs;
   E063's Arabic-B margin over controls is disclosed as seen beforehand).
6. **Bigger work:** a correction census from the images; a herbal–pharma match test using the forum's rated table
   (thread-4067, needs a login; exclude f102).

## 7. Published pages (private to Arham unless he shares them)
- **State of the evidence:** https://claude.ai/artifact/BkoDnrHQmXpUrq2aL4N3Qi (source
  `reports/artifacts/voynich_state.html`).
- **Word ledger** (searchable word-frequency table): https://claude.ai/artifact/DkNAGQMGyPWsCcyEFscWLB (source
  `reports/artifacts/voynich_word_ledger.html`).

## 8. Experiment index after the stop rule (E030–E073)
For E001–E029a see `reports/SUMMARY.md`.

| Exp | Result |
|---|---|
| E030 | Languages can double words (L up) |
| E031 | One Czech primer does both copy kinds (L × 3, fragile) |
| E032 | Timm generator fails 7/13 (M × 1/3) |
| E033 / E034 | No plain language or genre matches |
| E035 → E035b | Variation match withdrawn |
| E036 | Free invention matched by the rule (L × 10, C × 3), with caveats |
| E037 | Grammar profile |
| E038 / E039 | Sign inventory; scribe vs location |
| E040 / E041 | Cleaned profile; B at S3 |
| E042 | WALS + shortlist (Hebrew, Turkish top) |
| E043 | Line recurrence (C21) |
| E044 | Not syllable spacing |
| E045 | Human gibberish: INCONCLUSIVE |
| E046 | C21 widespread |
| E047 | Validated attack: GO |
| E048 | Word order: VOID |
| E049 | Attack: no claim |
| E050 | Hebrew near miss explained; blind reading |
| E051 | C21 on fresh languages (Tamil, Assamese); caution withdrawn |
| E052 | 7 more languages: no claim |
| E053 | Abbreviated Latin: no claim |
| E054 | Page topics: VOID |
| E055 | Same-label pairs: not shown |
| E056 | Not numbers |
| E057 / E058 | Per-word repeats: VOID, with a lean towards M |
| E059 | Clean-up: q- is a junction form after -y; d± not a scribe habit; e/ee differ at glyph level; pages cluster by sheet (C24); label echo is neighbourhood, not page |
| E060 | Ingredient link (pharma labels in recipes): VOID, Culpeper power control failed (wrong target window). Unscored: labels 71.1% vs matched 68.2%, p 0.24 |
| E061 | Stems vs padding: VOID (rule uncalibrated). Unscored: stem stream language-like (2,228 stems, 55% hapax), 6–8 sd from padding ciphers and generator |
| E062 | Verbose cipher with one table per scribe: CLASS FAILS (best 8/13 fails; repeats 0.9× vs 2.6×). C × 1/3 |
| E063 | Wide validated attack, 49 languages, A and B: NO CLAIM, 49/49 validated. L × 0.94, C × 0.96 (7 Indic languages were fragment streams) |
| E064 | Re-audit: E031 withdrawn (0/30 fresh languages do both) L × 1/3; five-scribe generator fails 7/13, E032 stands; E051 re-measured 0/30 with correct words, C21 caution reinstated |
| E065 | Syllable route go/no-go: NO GO (25 Voynich final classes vs 284–481 final syllables; syllable streams 826–1,499 types vs 6,077). L × 0.921 |
| E066 | Word individuality v3: VALID (4 languages separate); Voynich FAMILY-LEVEL z −1.2, generator-like. M × 3 (empirical ratio 1.4) |
| E067 | Human gibberish vocabulary at 150 tokens: LIKE VOYNICH (d +0.28); languages and generator d −1.6. M × 3 |
| E068 | Human gibberish on WLSD, H2, END5, R, NR: Voynich-like on 1 of 5 (NR). M RULED DOWN, M × 1/3 |
| E069 | Word-partner persistence across halves: Voynich 0.073, above all generator stretches (≤ 0.053), below 56/60 languages (p10 0.083). INCONCLUSIVE, no factor |
| E070 | Content-word partners (ranks 51–250): Voynich 0.004, below all 60 languages and the generator median; A-only safeguard fails by a hair. INCONCLUSIVE by rule; unscored lean to M; catalogue alternative untested |
| E071 | Label words as truncations: VALID (abbreviated Pliny z +14 to +16, planted z +12 to +21, 0 false claims); Voynich labels z +0.4. NOT ABBREVIATION-LIKE, L-abbrev × 0.6 (within L) |
| E072 | ot/ok as a detachable front piece: VALID; Voynich z +3.7 DETACHABLE, generator z +4.7 to +5.4 too. No factor; remainders starting with e never stand alone |
| E073 | Same-label zodiac figures alike? VOID (2 of 5 features reliable; kappa paradox on CLOTHED). Unscored same-label z −0.2: lean NO LINK |
