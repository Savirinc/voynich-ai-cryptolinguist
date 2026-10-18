# A first-principles methodology for the Voynich manuscript

Written 2026-10-18 after E001–E018. This is the plan every future experiment must fit into. It changes only by a
dated revision at the bottom.

## 1. The question, stated precisely

Decipherment = finding three things at once:

1. **Mechanism M**: how writing relates to language (plain alphabet, odd spelling, abbreviation, syllabary,
   verbose cipher, codebook, or no language at all).
2. **Unit map U**: which Voynich unit (glyph, glyph cluster, word, line) corresponds to which language unit
   (sound, letter, syllable, word).
3. **Language L**: which language, with what spelling.

A proposed (M, U, L) is correct if (a) it turns the *whole* text into probable language, consistently, and (b) it
predicts things it was never fitted to: the locked pages, the pictures, the labels.

### Correction to "only two possibilities"
Shannon's argument says that *if* the text is a cipher of a known language, a long enough text has only one
reading. It does not say the text *has* a reading. There are three doors, plus mixtures of them:

| Door | What it means | Can it be solved with certainty? |
|---|---|---|
| **1. Known language, hidden by a system** (cipher, odd alphabet, abbreviation) | Shannon applies: 28k words is far above unicity | **Yes**, if we test the right system class. This is what E017/E018 do |
| **2. A language we have no text for** (lost dialect, constructed language) | No language model exists, so Shannon gives nothing to compare against | **Only with anchors** (names, pictures, a bilingual), as with Linear B. Without them it stays like Linear A |
| **3. No language** (meaningless, made to look like writing) | Gaskell & Bowern (2022) had people write gibberish and found it statistically similar to Voynichese; Rugg (2004) and Timm & Schinner (2020) made generators. Our E013/E014 meaningless twins also fit many features | **Never with certainty.** Only made more or less probable |

The goal is therefore: **solve it if it's door 1, prove which door it is if not.**

## 2. What history teaches (our experience and everyone else's)

| Case | What worked or failed | Rule we take |
|---|---|---|
| **Linear B** (Kober, Ventris 1952) | Internal structure first (inflection triplets, the grid), then place names as anchors, then an independent test (tripod tablet) | Structure → anchors → independent confirmation |
| **Maya** (Knorozov 1952; Proskouriakoff 1960) | Landa's "alphabet" was a misunderstood syllabary. Names, dates and pictures carried the proof | Get the **unit** right first; anchors come from pictures and calendars |
| **Egyptian** (Champollion) | Bilingual text plus royal names in cartouches | Proper names are the strongest anchors |
| **Copiale cipher** (Knight, Megyesi, Schaefer 2011) | 75k-symbol homophonic cipher with nulls. Solved by statistics after first establishing which symbols carried letters | A strong solver inside the right model class succeeds quickly |
| **Zodiac Z340** (Oranchak, Blake, Van Eycke 2020) | Solved by **systematically listing** transposition schemes and running a proven homophonic solver on each | Enumerate the hypothesis space; one validated solver per cell |
| **Linear A, Rongorongo, Indus** | Too little text, no anchors, unknown language | Door 2 without anchors stays unsolved. Admit it |
| **Failed Voynich claims** (e.g. Newbold, Gibbs 2017, Cheshire 2019; partial readings such as Bax 2014) | No known-answer test, no controls, words picked to fit, only parts of the text read | Our rules (section 4) exist to rule out each of these failure modes |
| **Our E016 → E017 → E018** | Search luck mattered more than text length. The LM gap was a false success signal. Fixing both gave a proven tool, then a clean NO CLAIM on Voynich | Validate every attack on known answers *before* touching Voynich |

## 3. What the Voynich text itself tells us (facts, not theories)

- **Words are rigidly built.** Glyphs have fixed slots within words (Stolfi; Zattera 2022). Character-level
  predictability is unusually high (Bennett; Lindemann & Bowern 2020).
- **Word statistics look language-like:** Zipf's law, vocabulary growth, and section-specific "keywords"
  (Montemurro & Zanette 2013; our okeod- family is 3.5× concentrated in f67–f73).
- **Two "dialects"** (Currier A/B) and several scribes (Davis 2020).
- **Odd local habits:** adjacent near-repeats, line-start and line-end effects, glyph coupling across word
  boundaries (our E012/E013).
- **Possible anchors on the page:** month names in Latin script on the zodiac pages (probably added later, in a
  Romance language), labels next to plants, stars, nymphs and jars, the f116v marginalia, the f57v ring of 17
  glyphs repeated 4×, the single-glyph columns on f1r, f49v and f66r.
- **From E011–E018:** a verbose cipher with sandhi and nulls reproduces all 22 fingerprint features, but so,
  partly, do meaningless generators. The real Greshko tables leave 20% of Voynich words unparsed (true Naibbe
  text: ~5%). The validated attack makes **no claim** for Naibbe tables × la/it/fr/de.

## 4. The rules of evidence (fixed; they apply to every test)

1. **Pre-register** each test (question, data, procedure, decision rule), then lock it read-only and record its
   sha256 before the run.
2. **LOCKED_TEST pages are never read** until one final confirmation decode.
3. **Known-answer first:** any attack must crack synthetic texts of its own hypothesis class at Voynich length
   (≥ 80% of letters on ≥ 80% of keys), with every hidden part hidden (key *and* tables or inventory), before it
   is pointed at Voynich.
4. **Controls:** each validation includes meaningless twins (rugg, self-citation, letter-shuffled), attacked
   with every language model. Zero false claims are allowed.
5. **Two independent success signals:** independent restarts agree, and the decode is covered by real long
   words (E017). Others may be added, but only after validation.
6. **Whole text, not chosen words.** A reading must cover the text it is applied to, not a hand-picked sample.
7. **Independent confirmation:** the locked pages, plus agreement between pictures and text that the attack never
   saw.
8. Every result, including every NO CLAIM, goes in the ledger and is published.

## 5. The programme

The hypothesis space is a grid of **mechanism × unit map × language**. Testing every cell blindly costs too much,
so first come cheap tests that rule whole rows in or out. Then validated attacks on the surviving cells, in
order of plausibility × cost. Anchors are used throughout.

### Stage A — Discriminating tests (cheap; they shrink the grid)

**A1. Unit-size test: does a Voynich word carry a word, a syllable, or one or two letters?**
- **Idea:** topic words cluster ("burstiness"). If a Voynich word is a plaintext word, Voynich words should cluster
  by section as strongly as real words do. If it carries only 1–2 letters (Naibbe), clustering should be much
  weaker, because letter pairs are not topical. If it's a syllable, the result should fall in between.
- **Test:** compare a burstiness profile (section-specific keyword share, Montemurro–Zanette entropy measure) of
  Voynich against synthetic twins of each family, built from the same multi-topic source texts. Families:
  word = word, syllabic, Naibbe verbose cipher, meaningless generators.
- **Value:** this cuts the mechanism axis directly. It wasn't among our 22 features.

**A2. Meaning test: do the labels match the pictures?**
- **Test:** labels of the same or similar drawn objects (repeated plants, pharma jars against their herbal pages,
  zodiac nymphs across months) should be more similar to each other than chance. Labels should also appear in the
  page's own paragraph text more often than a matched null.
- **Value:** a positive result is strong evidence against door 3. A meaningless generator writing labels has no
  reason to track the pictures, unless a hoaxer did so deliberately, and that would itself be a measurable pattern.

**A3. Atom test: what are the real glyphs?**
- **Question:** which segmentation (e.g. `ch`, `sh`, `iin`, `aiin` as single units, or the `i` strokes as a count)
  makes the glyph statistics look like an alphabet or syllabary from some known script tradition (Lindemann & Bowern)?
- **Value:** this fixes U for the mechanisms where glyph = sound.

**A4. Mechanism signatures: which systems produce Voynich's odd local habits?**
- **Habits:** line-start and line-end effects, near-repeats, boundary coupling.
- **Test:** for each family, does it produce these habits as a by-product, or only when they are added on purpose?
  A mechanism that explains them for free is more probable.

Each Stage-A test is scored as a **likelihood ratio** between families, measured on twins. The posterior over the
doors and families is updated in a ledger table, so we always know where the probability sits.

### Stage B — Validated attacks on the surviving cells (Door 1)

These are in expected order. Each one needs its own E016/E017-style known-answer test first.

- **B1. Verbose cipher with LEARNED tables.** The attack infers which glyph strings are units (from slot grammar
  and parse coverage) together with the key. It's validated on twins whose tables are secret. This is the
  direct follow-up to E018, and the 20% unparsed rate points here.
- **B2. Natural language in an invented alphabet, with unknown spelling.** Glyph clusters (from A3) map
  many-to-one onto sounds or letters, with word spaces kept and a word-level LM. The closest relatives are
  E00x-type substitution attacks, now with A3's atoms and E017's search and claim rule.
- **B3. Abbreviated Latin or vernacular** (scribal shorthand: suspensions and contractions). The attack expands
  glyph groups into letter strings using an abbreviation model learned from real abbreviated manuscripts.
- **B4. Syllabary:** each glyph cluster is a syllable. LMs are trained over syllables.
- **B5. Codebook or nomenclator:** whole words stand for words. This is testable only through word-level
  structure and anchors; Shannon gives little here.

**Language axis.** Every attack runs over a widened library of 15th-century candidates, in period spelling:
Latin, Tuscan, Venetian, Lombard, Occitan, Catalan, French, Alemannic and Bavarian German, Czech, Hebrew, Greek,
Arabic and Middle English. Building these corpora is a work item of its own.

### Stage C — Anchors (Ventris's place names)

- **Use in DEV only, as soft constraints** (a "crib" score added to the search):
  - zodiac month labels against month names;
  - consensus plant identifications against plant names;
  - star and nymph labels;
  - f116v;
  - the f57v repeated ring as a possible key or alphabet list.
- **Test cribs on twins first.** A crib must help crack twins, and must not create false claims on meaningless
  controls.
- **Anchors also confirm.** A decode that names the drawn plant correctly on pages it was not fitted to is the
  modern tripod tablet.

### Stage D — Confirmation (the one-time unlock)

- **When:** only after a DEV claim that passes section 4.
- **Steps:**
  1. Decode the LOCKED_TEST pages once, with the frozen key.
  2. Pre-registered checks: the claim rule holds on those pages, labels match pictures, and month and plant names
     come out right.
  3. Independent readers check the decoded text without being told what to expect.

### Stage E — If Door 1 is exhausted

- **Door 2 (meaningful, but no known language claims):**
  - Linear B-style internal analysis: paradigm grids from word-ending alternations, with sound values fixed by
    anchors.
  - Honest expectation: it stays unsolved unless anchors are rich enough.
- **Door 3 (meaning test negative, and meaningless families favoured):** write up the probability case and stop.

## 6. What "certainty" can honestly mean

| Door | Strongest claim possible |
|---|---|
| **Door 1** | Near-certain, by Shannon. One key reads all 28k words, independent restarts agree, and the locked pages and pictures confirm it |
| **Door 2** | Strong only to the extent that anchors exist |
| **Door 3** | Probable, never proven: "every validated reading class failed, and labels don't track pictures" |

## 7. Immediate next steps (one at a time)

1. **A1 unit-size test.** Pre-registered; uses existing twin generators plus word-level and syllabic twins.
2. **A2 label–picture test.** Needs a curated label/object table: which labels sit next to which drawn objects, and
   which objects repeat. That table is built before looking at any decode.
3. **A3 atom test**, then build Stage B in the order A1–A4 suggest.

The same plan applies to the Indus script. There the corpus is short (about 4,000 inscriptions, about 5 signs
each), so the Shannon route is largely closed and it is a Door-2 problem: structure plus anchors.
