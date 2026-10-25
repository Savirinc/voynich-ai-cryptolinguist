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
- **He approves each test with "ok" or "yes".** Propose one next test at a time, with a clear recommendation, and wait
  for approval before pre-registering it.
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
6. **Check earlier reports first:** `reports/SUMMARY.md` (E001–E029a), `reports/LEDGER.md`, the reports E030–E062
   (`reports/CLEANUP_ROUND.md` is E059, `reports/INGREDIENT_LINK.md` E060, `reports/STEM_STREAM.md` E061,
   `reports/SCRIBE_TABLES.md` E062), and `reports/FORUM_SYNTHESIS.md` (what voynich.ninja already knows).
7. **Known answers first:** every attack must crack synthetic texts of its own class and make **zero false claims**
   on gibberish and wrong-language controls before it touches Voynich.
8. **Seed check:** any pass or fail within about 0.5 sd gets a seed-replicate check (≥ 8 of 10 seeds) before it is
   scored (lesson of E035/E035b).
9. **No model-hunting:** declare in advance how many variants a family gets. E036 closed the spelling-variation
   family; E058 closed the per-word-repeat family.
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

## 5. Where things stand (2026-10-25, after E062)
**Ledger** (`reports/LEDGER.md`): **M 0.0078, L 0.9815, C 0.0093, O 0.0013** (after E062).
- **M** = meaningless; **L** = a real language in its own script; **C** = cipher or code; **O** = other.
- **Honest range:** L is about 0.60–0.98; C about 0.01–0.05. L's lead rests partly on early tests (E030–E032).

**Two unscored cautions that lean towards M:**
- a 2026 generator (quimqu, voynich.ninja thread-6219) reproduces C9/C21;
- in E058, Voynich's words repeat as their *families* predict (z −1.1), like the generator, while Indonesian shows
  word-specific behaviour (+4.8).

**Sub-hypotheses:**
- L-sacred 0.30 / L-practical 0.45 / L-other 0.25 (shares of L; E043 gave no factor);
- SYLL-UNIT (spaces separate syllables) 0.08;
- ORDER-SCRAMBLED 0.15;
- NUMBERS (zodiac labels) 0.024.

**Forms of L** (`ABSENCE_RULE.md`):
- **L-alpha-known (0.35):** mostly searched, not found (10 languages);
- **L-syll (0.20):** untested;
- **L-abbrev (0.15):** abbreviated Latin searched, not found;
- **L-unattested (0.20)** and **L-other (0.10)**.

**Validated attack (E047; VOY23 class)** — Voynich A's 23 commonest signs (cleaned EVA, S3 units), homophones, 12%
spelling slips, many-to-one annealing with a 4-gram KN LM with spaces. Claim requires:
- agreement ≥ 0.95;
- lexrate ≥ a calibrated threshold;
- beating pseudo-Voynich and generator controls.

**Searched, not found:** Hebrew, Turkish, Latin, Czech, Serbian-Croatian, Slovak, Ukrainian, Romanian, Italian,
Romani (E049–E052); abbreviated Latin, technical and sacred (E053).
- The Hebrew "near miss" (E049) was explained by pseudo-Voynich controls.
- Blind judges called the Hebrew decodes word salad while identifying real Hebrew (2 Kings 22) (E050).

**Measured facts** (full list in LEDGER, C1–C24):
- **Physical and dating:** vellum 1404–1438; five scribes.
- **Vocabulary:** 7,060 DEV word types, 69% hapax, 149 words make up half the text.
- **Units:** glyph-level predictability is below all alphabets, and simple-syllable-like only with glyph groups.
- **Endings:** about 21–28, combining freely with stems.
- **Line recurrence:** words recur within lines, with no avoidance of back-to-back repeats (AS ≈ 1). Of about 90
  meaningful texts, only languages with echo or doubling grammar reach this (Indonesian, Tamil, Assamese).
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

**Re-test queue from the forum sweep** (`FORUM_SYNTHESIS.md`): E059 settled the first three (line position, e/ee/eee
glyph contexts, bifolio session effect; all confirmed, facts corrected). Still open: C3 depends on glyph grouping.

## 6. Next steps (recommended order; propose one at a time)
1. ~~Clean-up round~~ done (E059, `CLEANUP_ROUND.md`).
2. **Re-audit the early ledger factors (E030–E032)** under today's evidence (generator progress, E051, E058), as a
   pre-registered audit, not hand edits.
3. **Cheap leads:**
   - score the published Naibbe ciphertexts (pykeedy) on our battery;
   - where near-copies come from (first occurrence vs proximity vs neither), controlling for sheet;
   - ending agreement between neighbouring words (q- after -y is now known; test the rest);
   - the zodiac shed-/ched- by sign gender;
   - p vs f (f57v ring).
4. **Syllable route:** Vietnamese with tones as a final letter; pfeaster's syllable-per-word hypothesis on European
   text (the go/no-go is about 6,000 types per 28.8k tokens).
5. **Constructed-language controls** (Enochian, Lingua Ignota), and an Arabic abjad attack (words of 4+ glyphs).
6. **Bigger work:** a correction census from the images; a herbal–pharma match test using the forum's rated table
   (thread-4067, needs a login; exclude f102).

## 7. Published pages (private to Arham unless he shares them)
- **State of the evidence:** https://claude.ai/artifact/BkoDnrHQmXpUrq2aL4N3Qi (source
  `reports/artifacts/voynich_state.html`).
- **Word ledger** (searchable word-frequency table): https://claude.ai/artifact/DkNAGQMGyPWsCcyEFscWLB (source
  `reports/artifacts/voynich_word_ledger.html`).

## 8. Experiment index after the stop rule (E030–E058)
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
