# The Voynich Manuscript, weighed by Bayes' rule: what we did and where it stands

*Arham Partap Jain / Savir Platforms, with Claude (Anthropic). 15 October – 1 November 2026. MIT licence.*

> **Bottom line.** After about 120 pre-registered experiments we have **not read a single word** of the Voynich
> Manuscript, and we do not claim to.
> - **Where the evidence points:** the text behaves far more like the product of a careful, rule-following but
>   *meaningless* writing process than like a language or a cipher. Our running estimate is **M 0.91, L 0.06, C 0.01,
>   O 0.01**.
> - **What no one has done:** build a meaningless process that reproduces everything the manuscript does. We tried;
>   our best reproduces about half.
> - **So this is not a verdict.** It is a ledger that stays open. When new evidence arrives, the numbers move.

---

## 1. How we decide: Bayes' rule in one paragraph

We keep four hypotheses alive at once:

| | Hypothesis | Meaning |
|---|---|---|
| **M** | Meaningless | Text produced by a process (copying, tables, habit) that carries no message |
| **L** | Language | A real language written in its own script, known or lost |
| **C** | Cipher or code | A known language hidden by a system |
| **O** | Other | Anything else (e.g. a mixture, a ritual procedure) |

Each hypothesis has a probability, and all four add up to 1. A test is chosen so that the hypotheses predict
*different* outcomes.
- **When the result comes in,** we multiply each hypothesis by how well it predicted the result (its *likelihood
  ratio*, or "factor"), then rescale so the four add to 1 again. That is all Bayes' rule is.
  - A result that is three times likelier under M than under L multiplies M by 3.
  - A result no hypothesis predicts better than another changes nothing.
- **Absence counts.** If a search that we *proved* could find something finds nothing, that is evidence too (the dog
  that didn't bark).

**Rules that keep us honest** (full list in `CLAUDE.md`):
1. **Pre-registration.** The question, data, decision rule and Bayes factor for every outcome are written down, locked
   read-only and hashed (sha256) *before* the test runs.
2. **Known answers first.** Every attack must crack synthetic texts of its own kind, and make no false claims on
   gibberish, before it is pointed at the manuscript.
3. **Locked pages.** 15 leaves (text and images) have never been touched. They are kept for one final confirmation.
4. **No model-hunting.** The number of variants of a test is declared in advance.
5. **Failures are published.** Every null, every void test and every withdrawn claim stays in `reports/LEDGER.md`.
6. **Symmetry.** "Meaningless" must face tests it can *win*, as strongly as "language" does.

---

## 2. The story, phase by phase

### Phase 1: tools and first attacks (15–20 Oct; E001–E029)
- **Transcription:** we parsed the standard ZL3b transcription and split it by physical leaf. That gave 85 working
  (DEV) leaves and 15 locked leaves.
- **First validated attack:** we built and validated a cipher attack (8/8 known answers cracked, 0 false claims in 32
  controls). It found nothing in the manuscript.
- **Basic shape of the text:** words behave like word-sized units; no grouping of signs behaves like an alphabet; the
  line is a unit. (`reports/SUMMARY.md`)

### Phase 2: language surges, then is checked (21–25 Oct; E030–E070)
- **The surge:** early tests seemed to favour language strongly. Real languages also double words (E030), and a
  spelling-variation match was found (E035/E036). The ledger reached **L 0.97**.
- **The letter-cipher attack, on a large scale:** validated, then run against about 60 languages letter by letter
  (Hebrew, Turkish, Latin, Czech, Arabic, German and many more), on both "dialects" of the manuscript (Currier A
  and B). **No language was found** (E049–E063).
- **The first tests M could win:**
  - the manuscript's words repeat as their *shape families* predict, as a machine's would (E066);
  - its vocabulary at 150 words matches people asked to write gibberish (E067).

### Phase 3: the pieces of words, labels, and the Hebrew campaign (26–27 Oct; E071–E085)
- **Word pieces:** words are built from a front, a middle and an ending; 60 pieces write 64% of the text.
- **Labels:** label words are not abbreviations (E071), not numbers (E056) and not tied to their pictures (E073, E085).
- **The Hebrew campaign:** six Hebrew forms tested, none found.

### Phase 4: checking ourselves (28 Oct; E086–E093)
- **Power check (E090):** the letter attack cracks real technical texts, but its "is this a real word?" gate missed
  some. The absence factors were too strong and were corrected.
- **Ledger audit (E091):** two early language-favouring results had lost their basis and were **withdrawn**. The
  ledger fell from L 0.88 to **M 0.46 / L 0.36**: an honest correction, not new data.
- **Transcription check (E092):** four core facts survive a change of transcription; one ("spaces are mechanical")
  depends on how glyphs are cut.

### Phase 5: cribs and period ciphers (28–30 Oct; E094–E098)
- **Zodiac cribs:** month names and sign meanings were used as cribs (known words at known places). The tests were
  void or found no link (E094–E096). A lesson: AI sub-agents recognise the manuscript, so they cannot serve as blind
  judges.
- **One key for the whole book:** ten period languages mixed by line found nothing (E097).
- **Period cipher designs:** five designs (nomenclator, nulls, rotating tables, abbreviation plus cipher, in-word
  sorting) do not reproduce the manuscript's statistics (E098).

### Phase 6: the community's ideas and Shannon's questions (30 Oct – 1 Nov; E099–E121)
Ideas collected from Reddit were each turned into a pre-registered test.

- **Phrases:** real texts reuse phrases. Against controls matched for vocabulary richness, the manuscript sits *between*
  language and the gibberish generator. It has **no repeated four-word phrase at all** (E099, E100).
- **Word-pair order:** pairs of words appear in either order about equally often, the way a generator's do (E104,
  M × 3).
- **Dice-built words** fail (E114). This is a strike against one meaningless process.
- **Five "Shannon moves"** (asking where the information is, not what the text resembles):
  1. **How far the link between words reaches:** no yardstick separates language from gibberish at this length.
  2. **Merging the five spelling families** still gives no phrases (E116, M × 3).
  3. **Where the surprise sits:** at paragraph openings, line ends and labels, but this does not separate language
     from gibberish.
  4. **Can any attack ever work?**
     - Letter ciphers: yes, the key comes out from about 125 words, and the manuscript is 70 times longer.
     - Whole-word codebooks: **never**. Wrong codebooks fit as well as the right one, so only outside clues can test
       them (E118).
  5. **Labels as name-cribs:** label words are not introduced at paragraph openings as names are (E119, M × 1.5).
- **Building a meaningless process (E120):** our best "habit writer" reproduces 5 of 10 held-out facts. **It fails**
  (M × 0.9).
- **Correction census (X121):** 16 marked corrections in 28,841 words, all glyph-level. No skipped word was ever
  added back.
- **An open-web sweep** by five research agents (`reports/WEB_SWEEP.md`) found new leads to test. Among them: a 2026
  paper that cannot exclude two-key ciphers, and evidence that the book was written on loose sheets.

---

## 3. How the numbers moved

| Date | After | M | L | C | O | Why |
|---|---|---|---|---|---|---|
| 21 Oct | E031 | 0.13 | 0.79 | 0.06 | 0.01 | Languages double words; one primer does both kinds of copying |
| 21 Oct | E036 | 0.006 | **0.970** | 0.023 | 0.001 | Spelling variation matched (later withdrawn) |
| 25 Oct | E067 | 0.19 | 0.78 | 0.02 | 0.004 | Human gibberish matches the vocabulary |
| 28 Oct | E091 audit | **0.46** | 0.36 | 0.10 | 0.08 | Two early results withdrawn; honest reset |
| 30 Oct | E098 | 0.49 | 0.36 | 0.07 | 0.08 | Period cipher designs fail |
| 31 Oct | E104 | 0.74 | 0.18 | 0.03 | 0.04 | Word pairs have no preferred order |
| 1 Nov | E116 | 0.89 | 0.08 | 0.02 | 0.02 | Still no phrases after merging spellings |
| 1 Nov | E120 | **0.91** | 0.06 | 0.01 | 0.01 | Best meaningless process fails (M slightly down) |

**How far to trust these numbers.**
- **The factors are judgement calls.** Each one (× 3, × 1.5, × 0.9) was fixed before its test, but not measured.
- **The swings are part of the record.** The early surge to L 0.97 rested on results we later withdrew.
- **What is robust is the direction since the audit:** almost every test that could go either way has gone M's way.
- **What is not established is "meaningless" as a fact.** M is ahead because language signals are *missing*, not
  because anyone has shown how the text was made.

---

## 4. Where we stand

**Measured facts** (they hold across transcriptions):
- no repeated phrases, even after spelling variants are merged;
- words behave by shape family, not individually;
- lines do not continue each other;
- near-copies of nearby words through five small spelling swaps;
- pages on the same vellum sheet share habits;
- labels do not behave like names.

**Excluded, within stated limits:**
- letter-by-letter ciphers of about 60 known languages (proven attackable);
- six Hebrew forms, a syllable script and abbreviated Latin labels;
- several period cipher designs;
- the published copy generator, dice-built words and human gibberish (each fails).

**Open:**
- whole-word codebooks (untestable without outside clues);
- two-key ciphers with heavy miscopying (`WEB_SWEEP.md` #1);
- a lost or invented language;
- a meaningless process that nobody has yet built well enough.

---

## 5. What evidence would move the numbers (we are waiting for it)

| New evidence | Moves |
|---|---|
| A meaningless process that reproduces all solid facts, including phrase reuse, sheet sharing and page-opening surprise | M up strongly |
| A crib (a word from a picture) that predicts text on pages it was not fitted to | L or C up strongly |
| A two-key or word-class cipher that fits our battery and the held-out facts | C up |
| An ordering signal in a quire that copying cannot produce (cf. Quire 20, `WEB_SWEEP.md` #3) | L up |
| Correction rates from 15th-century copied herbals and from handwritten gibberish | Turns the correction census into a scored test |
| New imaging (multispectral, XRF) showing erased or rewritten *words* | L or C up |
| A bilingual, a key, or an external document | Decisive |

Anyone can add evidence: write the test down first, prove it on known answers, then run it. The ledger
(`reports/LEDGER.md`) records every step.

---

## 6. Reproduce it
- **Code:** `experiments/` (one script per test).
- **Pre-registrations:** `reports/E0NN_PREREG.md`.
- **Results:** `experiments/results/`.
- **Reports:** `reports/`. Start with this file, then `reports/SUMMARY.md` (Phase 1), `reports/LEDGER.md` (every
  factor) and `CLAUDE.md` (rules and index).
- **Environment:** Python 3.11 (`.venv`); external texts are listed in `CLAUDE.md` §4 and are not redistributed.
