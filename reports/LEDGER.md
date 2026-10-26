# The Voynich ledger: what is certain, what is excluded, and how likely the rest is

Started 2026-10-21, agreed with Arham ("yes"). This is a living file. The **starting point** (sections 1–4) was fixed
on 2026-10-21, and its sha256 is in the commit that created this file. After that, sections 1–4 are changed only
by an entry in the update log (section 6) that cites a test. Nothing is edited silently.

## 0. Declared deviation: the search continues past the stop rule
The stop rule in `reports/FINAL_ROUND.md` (locked) was triggered on 2026-10-21 by E029a (`reports/WORD_REPEATS.md`),
and the final report `reports/VOYNICH_FINAL.md` was written. Arham then chose to continue ("I am not ready to leave
the voynich hustle as yet"). That is his decision, and it is recorded here as a deviation.

This ledger replaces the stop rule as the guard against loops: **a test is run only if, stated in advance, its
outcome would move at least one probability in section 4.**

## 1. Certain: measured facts
These are facts about the text as transcribed in EVA, measured on DEV, with LOCKED_TEST untouched. They are
certain *as measurements*. What they mean is not. They also rest on the transcription's reading of glyphs and word
spaces.

| # | Fact | Source |
|---|---|---|
| C1 | The vellum is radiocarbon-dated to 1404–1438. This is external, at 95% confidence. The ink and the writing are not dated directly | Univ. Arizona, 2009 |
| C2 | Glyphs are very predictable inside words: h2 2.10–2.48, against ≥ 2.79 for all 34 comparison languages written in letters | E002, E024 |
| C3 | With glyph groups read as units, h1, h2 and word length fall inside the range of simple-syllable languages (nearest: Mandarin pinyin) | E027 |
| C4 | The vocabulary is as rich as Latin's: 6,077 distinct words in DEV, 68% seen once | E028 |
| C5 | About 28 endings, only partly written with their own glyphs | E026 |
| C6 | Strong line-start and line-end habits | E025 |
| C7 | Words cluster by topic (I_word 0.387, inside the word-family range) | E019 |
| C8 | Common words persist across the text the way grammar words do (PERS_30 0.264) | E021 |
| C9 | A word sits next to a copy of itself in 0.95% of within-line pairs. That is 2.3× what chance gives for Voynich's word frequencies; Latin gives 0.02–0.28× chance. Near-copies (one glyph different) appear in 3.65% of pairs, against 0.4–2.1% in Latin. The repeats are spread over 97 word types | E029a, plus an exploratory look on 2026-10-21 |
| C10 | Currier A and B differ in statistics but share these properties (e.g. repeat rate 0.97% vs 0.95%) | E011, E029a |

## 2. Excluded: logical exclusions, each within its stated scope
| # | Excluded | Scope | Source |
|---|---|---|---|
| X1 | A simple letter substitution, with any key | 34 comparison languages, 9 glyph groupings | E012, E019, E021, E024 |
| X2 | A Naibbe-type verbose cipher (each word = 1–2 plaintext letters), with any table | la/it/fr/de | E016–E019 |
| X3 | Any word-for-word code (syllable notation, codebook, stem + ending, plain reading), with any table or homophones | ordinary la/it/fr/de prose | E029a |
| X4 | Our Rugg-grille and self-citation generators **as implemented** | those two programs only, not the idea of meaningless text | E011, E019, E021 |
| X5 | A one-syllable-per-word language written plainly (Hawaiian, Tongan, Māori, Vietnamese, Mandarin types) | vocabulary far too small | E028 |

## 3. The hypotheses
The four hypotheses are mutually exclusive and together cover every possibility.

| | Hypothesis | Includes |
|---|---|---|
| **M** | Meaningless, made by a human habit | Copy-and-change writing, glossolalia, a hoax |
| **L** | A real language written plainly in its own script, apart from the excluded scopes | Agglutinative or simple-syllable languages; a plain script with glyph-group spellings |
| **C** | A cipher or code over a real language, apart from the excluded scopes | Mixed systems (code plus fillers), other plaintext languages, abbreviation-based systems |
| **O** | Other | Invented language, private shorthand with no recoverable language, something not listed |

## 4. Starting probabilities (fixed 2026-10-21)
These are judgement, already informed by E001–E029a. They are not measurements.

| | Point | Range we would not argue with |
|---|---|---|
| M | 0.45 | 0.30–0.60 |
| L | 0.30 | 0.15–0.45 |
| C | 0.20 | 0.10–0.30 |
| O | 0.05 | 0.02–0.10 |

Why these numbers:
- **M is highest.** C9 (words attracted to copies and near-copies of themselves) is the signature of copy-and-change
  writing, and the exclusions X1–X3 removed the most likely cipher designs. M is not higher because our generators
  failed (X4), and because C7 and C8 look language-like, though no good generator has been tried.
- **L is second.** C3 is fitted by simple-syllable languages, and C4 and C5 suggest word-building. Against L: every
  language we measured avoids putting a word next to itself (C9). Languages with reduplication have not been
  measured.
- **C is lower.** X1–X3 removed the simple versions over the likely languages, so what is left is more complex,
  and so less likely a priori (Occam).

## 5. How the ledger is updated (Bayes)
- **Before each test**, in its pre-registration, we write down how likely each outcome is under each hypothesis. A
  coarse scale is enough: "expected", "possible", "surprising", "near impossible".
- **The Bayes factor** is the ratio of those likelihoods, read on a fixed scale:

  | Strength | Bayes factor |
  |---|---|
  | weak | 3 |
  | moderate | 10 |
  | strong | 30 |
  | decisive | 100 |

  It is applied as: new odds = old odds × Bayes factor. Factors larger than 100 are not used, because the
  assumptions behind any test cap how far it can move us.
- **A test moves a hypothesis to "excluded"** (section 2) only by logical exclusion with a stated scope, never by
  probability alone.
- **Sensitivity:** each update is reported twice, from the point values and from the edges of the ranges. If the
  conclusion flips inside the ranges, we say so.
- **Gate:** a test whose outcome could not move any hypothesis by at least a factor of 3 is not run.

## 6. Update log
| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | starting point | — | — | 0.45 | 0.30 | 0.20 | 0.05 |
| 2026-10-21 | E030 reduplication (`REDUPLICATION.md`) | LANGUAGES CAN DO IT: Indonesian R 3.03, Malay 1.71 vs Voynich 2.65 | L × 3 | 0.28 | 0.56 | 0.13 | 0.03 |

**Sensitivity of E030.** Starting from the range edges M 0.60 / L 0.15 / C 0.20 / O 0.05, the result is M 0.46,
L 0.35. Starting from M 0.30 / L 0.45, it is M 0.18, L 0.73. **The M-versus-L ranking flips inside the agreed
ranges**, so neither is clearly ahead yet. C9 (word repeats) no longer counts against L. It now counts only against
languages that do not double whole words.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E031 copy pairs (`COPY_PAIRS.md`) | A LANGUAGE DOES BOTH, but only 1 of 153 texts: a Czech children's primer with spelling drills | L × 3 | 0.13 | 0.79 | 0.06 | 0.01 |

**Fragility of E031.** The update rests on one drill text. Had it not counted, the result would be M × 3, giving
M 0.54, L 0.36. Read L's lead as "real-language Voynich is only possible as a drill, list or abbreviation-type text",
not as "Voynich is probably a language".

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E032 authors' generator (`COPY_GENERATOR.md`) | FAILS 7 of 13: matches copies, near-copies, h2, topic clustering and endings; fails vocabulary size and spectrum, and persistence | M × 1/3 | 0.05 | 0.87 | 0.07 | 0.01 |

**Reading after E032.**
- The chain E030 → E031 → E032 moved L up mainly by **removing objections** to it. Nothing so far shows that any real
  language text matches Voynich on all 13 features.
- Without the Czech primer (E031 fragility), the figures would be M 0.28, L 0.56, C 0.13, O 0.03.
- L's high number should therefore be read as "the best surviving explanation", not as "likely confirmed".
- The next test is the symmetric one: put real-language texts through the same 13 features.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E033 languages on 8 spelling-independent features (`LANGUAGE_FEATURES.md`) | PARTIAL: best Swahili and Latin fail 2 (R, Zipf); Indonesian fails 3; generator fails 6 | none | 0.05 | 0.87 | 0.07 | 0.01 |

**New certain fact C11 (E033):** Voynich's Zipf slope over its 100 most common words is −0.65. That is flatter than
all 12 Bibles (−0.79 to −1.12) and than the E032 generator (−0.82). No text yet combines Voynich's repeats, its rich
vocabulary and its flat Zipf head.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E034 practical/list-type texts (`GENRE_FEATURES.md`) | NO MATCH: best (Apicius + Cato + Varro) fails 3 (R, types, Zipf); Columella 5, Culpeper herbal 4 | none (pre-registered) | 0.05 | 0.87 | 0.07 | 0.01 |

**After E034.**
- Genre does not explain C9 + C4 + C11.
- The flat Zipf head is matched by no text measured: 12 Bibles, 3 practical texts and the copy generator.
- Candidate mechanism, not yet tested: free spelling variation of words, in a language that doubles words.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E035 spelling variation (`SPELLING_VARIATION.md`) | VARIATION MATCHES (narrowly): Indonesian + free spelling variation (α = 1.5, fitted on types only) fails 1 of 9 (type_hapax). Zipf −0.68 and NR 2.11 predicted. PERS_30 passes at z −2.98. Malay fails 4 | L × 10, C × 3 | 0.006 | 0.970 | 0.023 | 0.001 |

**After E035.**
- **First positive match.** A real language that doubles words, with common words spelled several ways, reproduces
  8 of 9 Voynich word features, including the flat head (C11) and the near-copies. Only one parameter was fitted.
- **The margin is thin.** Persistence passed by 0.02 sd, and the result rests on one text, Indonesian; Malay fails
  4. A rerun with other seeds could give PARTIAL.
- **Two remaining gaps:**
  - Voynich has more words seen once (0.68 vs 0.58).
  - It persists less.
- **Fragility, carried forward.** Without the Czech primer (E031), E035 gives M 0.04, L 0.89, C 0.06, O 0.005. The ranking
  no longer depends on E031.
- **What this narrows.** The working picture is now a text in a language with word doubling, written with free,
  unstandardised spelling, or something with the same statistics (C, via glyph homophones). This describes the
  *kind* of writing, not its content.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E035b seed replicates of E035 (`SEED_REPLICATES.md`) | NOT REPLICATED: 1 of 10 replicates match. Indonesian fails hapax in 10 of 10 and PERS_30 in 8 of 10 | correction L × 1/10, C × 1/3 (E035 withdrawn) | 0.054 | 0.868 | 0.069 | 0.009 |

**After E035b.**
- E035's match was a lucky seed, and its factor is withdrawn. The ledger is back to its post-E034 state.
- **Kept as an unscored observation:** spelling variation on a doubling language reproduces the flat Zipf head and
  the near-copies in every run.
- **Still unmatched:** Voynich's high share of words seen once (0.68) combined with low persistence (0.26).
- **Lesson for the method:** any result that passes by less than about 0.5 sd gets a seed-replicate check before it
  is scored.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-21 | E036 free invention of spellings (`FREE_INVENTION.md`) | ROBUST MATCH by the rule: Indonesian + fresh one-off spellings (p = 0.12) fails 1 of 9 in 9 of 10 seed runs (always the Zipf head). PERS_30 passes only through the wide window sd (0.48 vs 0.26) | L × 10, C × 3 | 0.006 | 0.970 | 0.023 | 0.001 |

**After E036, read with care.**
- **Persistence:** tolerated, not matched. The seed check could not test it, because the windows are fixed.
- **The two variation models each fit half:**
  - E035 (reused spellings) fits the flat head and misses the one-off words;
  - E036 (fresh spellings) fits the one-off words and misses the flat head.
- **No third model will be scored** (E036_PREREG).
- **Discount for two tries:** at ×3 instead of ×10, the values would be M 0.02, L 0.95, C 0.025, O 0.003.
- **Without the Czech primer (E031):** M 0.04, L 0.89, C 0.06.
- **In every version, L leads as "best surviving explanation".** What survives is the *kind* of writing: a
  doubling language with unstandardised spelling. Nothing about its content is known.

**Measured facts from E037** (working assumption L; no ledger change; `GRAMMAR_PROFILE.md`)
- **C12:** neighbouring near-copies differ at no special place in the word (ENDZ 0.98). They are mostly five
  alternations: e/ee, r/l, d±, q±, t/k.
- **C13:** doubled words are frequent, ordinary suffixed words (ρ +0.44; Indonesian +0.19), and avoid line starts
  (0.31, with a line-start vocabulary confound).
- **C14:** about 28 endings combine almost freely with stems: about 10 endings per stem, and the stem barely decides
  the ending (I_EXCESS 0.32). This is unlike Indonesian, Malay, Latin and Swahili. Currier A and B have the same
  shape.

**Measured facts from E038** (working assumption L; no ledger change; `SIGN_INVENTORY.md`)
- **C15:** *e* and *ee* are one sign written two ways (FREE VARIANT, calibrated on Latin controls).
- **C16:** *r* and *l* are not interchangeable. Words differing only by r/l have different neighbours (t_nbr −0.48).
- **C17:** forms with and without *d* sit on different pages (t_page 0.05), a section or scribe split. *q*-forms
  share neighbours with plain forms and are twice as common inside Currier B lines as inside A lines.
- **Positional forms (Arabic-type):** the test was VOID (its control failed), so the question is open.

**Measured facts from E039** (working assumption L; no ledger change; `SCRIBE_HABITS.md`; controls passed)
- **C18:** the d± form depends mainly on the scribe (13% of form uncertainty). Scribe 1 (Currier A) uses d-forms 23%
  of the time, scribes 2 and 5 56–59%. This is a scribe or dialect habit, and part of what makes A differ from B.
- **C19:** the q± and r/l forms depend on location within the book, not on the scribe. Given the word, scribes 1–3
  use q equally (44–45%).
- **Correction:** E038's "q twice as common in B" reflects B's vocabulary, not a B habit of adding q.

**Measured facts from E040** (cleaned inventory, e-runs → e and t → k; `CLEAN_PROFILE.md`)
- **C20:** after cleaning, Currier A stays inside the simple-syllable range (h2 2.33). Currier B falls below it (2.04,
  already 2.22 raw), and DEV sits just below (2.22). B is more predictable within words than any sampled language.
- **C11 revised:** the flat Zipf head survives cleaning for DEV (−0.74), but B alone is −0.84, inside the Bible
  range. The flatness is largely A/B vocabulary mixing plus spelling variation, not a property of each variety.
- **C4 confirmed:** cleaning removes 16% of distinct words. The share of words seen once is unchanged (0.66).

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-23 | E043 line recurrence by text type (`LINE_RECURRENCE.md`) | NOTHING MATCHES (sacred, practical, other, generator); Indonesian reference within tolerance | none | 0.006 | 0.970 | 0.023 | 0.001 |

**Sub-hypotheses of L (introduced in E043_PREREG):** L-sacred 0.30, L-practical 0.45, L-other 0.25 (shares of L).
These are unchanged after E043.

**C21 (E043):** Voynich does not avoid putting the same word back to back (AS 1.01). Every ordinary text strongly
avoids it (0.00–0.26). Latin hymns (refrains) reach 0.53, the copy generator 0.76, and Indonesian (real doubling)
1.45.

**C9 restated:** the excess of repeats is same-line recurrence (A 1.76, B 2.21 × chance), with no adjacency
avoidance. It is not back-to-back doubling as such. DEV's 2.6 is inflated by pooling the A and B vocabularies.

**Spacing sub-hypothesis (E044_PREREG):** WORD-UNIT 0.8 / SYLL-UNIT 0.2 → after E044 (SYLL-UNIT × 1/3) **0.92 / 0.08**.
Syllable-spaced Vietnamese and Chinese also avoid adjacent identical units (AS 0.25–0.31), and have far too few
distinct units. C21 (AS ≈ 1) is not reproduced by any writing system or text type tested. The nearest are
grammatical doubling (Indonesian 1.37, vocabulary too small) and the copy generator (0.76).

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-23 | E045 human gibberish vs C21 (`HUMAN_GIBBERISH.md`) | INCONCLUSIVE: gibberish AS 0.66 (95% 0.41–0.96), Voynich A 1.04; 68 meaningful texts max 0.52 | none | 0.006 | 0.970 | 0.023 | 0.001 |

**Unscored caution after E045.** On C21 the ordering is: meaningful texts (≤ 0.53) < human gibberish (0.66) < copy
generator (0.76) < Voynich (1.0) < grammatical doubling (about 1.4). Apart from doubling-grammar languages, no
meaningful text of about 90 comes near, whereas non-meaningful sources get most of the way. C21 leans towards M, and
the L lead was built without it. The rules allow no factor here, but anyone reading L = 0.97 should weigh this.

**E046 (measurement):** C21 is WIDESPREAD.
- AS 0.89–1.16 for all three main scribes.
- No clustering over 152 pages (p = 0.95).

It is a whole-book writing property, not a local list effect. The post-E045 caution stands.

**E047 (method validation):** GO. 9/9 Hebrew, Turkish and Latin ciphers in a Voynich-like 23-sign script were cracked
and claimed, with 0 false claims. Generator controls reach lexrate 0.42 against the threshold 0.514 (the narrowest
margin).

**E048:** VOID by rule (verse texts also have low order information). ORDER-SCRAMBLED stays at 0.15.
- Unscored: Voynich order information is about 7 sd above scrambled.
- It is weak: A sits with Latin hymns and the generator (Q about 0.2), B with Hebrew Psalms (about 0.35).

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E049 validated attack on Voynich A/B (`ATTACK_VOYNICH.md`) | NO CLAIM. Turkish and Latin: searched, not found. Hebrew on A: near miss (lexrate 0.542; bar 0.572; controls max 0.472; real cracks 0.65–0.79) | none | 0.006 | 0.970 | 0.023 | 0.001 |

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E050 Hebrew near miss (`HEBREW_NEARMISS.md`) | Part 1: Voynich A (0.542) inside the pseudo-Voynich range (0.507–0.550). Part 2: blind judges valid (real Hebrew scored 9–10, even identified), Voynich pages 1–1.5 like the fakes: NOT DETECTED | none | 0.006 | 0.970 | 0.023 | 0.001 |

**Searched, not found (validated VOY23 class):** Hebrew, Turkish and Latin, each written letter by letter in a
23-sign script with homophones, spelling slips and intact word order. This is empirical (with power 9/9 on known
answers and a blind reading), not a logical exclusion.

## Amendment: absence accounting (`ABSENCE_RULE.md`, sha256 05203b95de7348c39400789301839cf30369f464027d5097040b76e4d5dc1261)
A validated search that finds nothing now lowers the searched form: × (1 − s(1 − m)), with default m = 0.2.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | Absence accounting for E049–E050 (Hebrew, Turkish and Latin letter by letter, not found) | L-alpha-known(he, tr, la) share 0.1225 of L; C substitution of these 0.10 of C | L × 0.902, C × 0.92 | 0.0066 | 0.9688 | 0.0234 | 0.0011 |

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E051 missing-evidence audit (`MISSING_EVIDENCE.md`) | C21 on fresh data: 2 of 30 new languages (Tamil 1.01, Assamese 0.87) reach Voynich's AS; 0 of 10 fresh generator samples (max 0.81); BF(M:L) 0.56 | none | 0.0066 | 0.9688 | 0.0234 | 0.0011 |

**Correction:** the unscored caution after E045 ("C21 leans towards M") is **withdrawn**. On fresh data, real languages
with echo or doubling grammar reach Voynich's level, and the generator does not.

**New facts:**
- **C22:** zodiac nymph labels mostly do not repeat across months (29% vs ≥ 50% for day numbers). They are not a
  calendar of numbers.
- **C23:** label words occur in their own page's text 1.7× more than frequency-matched words.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E052 validated attack: Czech, Serbian-Croatian, Slovak, Ukrainian, Romanian, Italian, Romani (`SHORTLIST_ATTACK.md`) | All 7 VALIDATED (cracks ≥ 0.999); Voynich A at or below the fakes in every language: NO CLAIM | absence rule: L × 0.885 | 0.0074 | 0.965 | 0.0263 | 0.0012 |

**Searched, not found (VOY23), cumulative:** 10 languages, 0.79 of L-alpha-known.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E053 abbreviated Latin, technical and sacred (`ABBREV_LATIN.md`) | Both VALIDATED; Voynich A no better than the fakes: NO CLAIM | absence rule: L × 0.958 | 0.0077 | 0.963 | 0.0274 | 0.0013 |

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E054 page-topic boundaries (`PAGE_TOPICS.md`) | VOID: the copy generator also shifts topic at its page breaks (D 0.72); Voynich herbal A D 0.47; Culpeper 0.80 | none | 0.0077 | 0.963 | 0.0274 | 0.0013 |

**Deviation (2026-10-24, picture route).** While fetching the second panel of fold-out f101v (Beinecke canvas
"101v (part) and 102r"), a mis-estimated crop also contained **f102r, a LOCKED_TEST leaf**, and its image was
displayed once. No text from f102r was transcribed, decoded or used in any analysis. The file was deleted at once,
and the f101v panel was re-cropped to stay left of the gutter. The locked leaves' text remains unseen by every
attack and model. Images of locked leaves will not be downloaded again, and crops are now taken only from the left
page with a margin.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E055 same-label pharma drawings (`SAME_LABEL_PAIRS.md`) | NOT SHOWN: same-label pairs 2.17 vs controls 2.40 (identity checks 9.9); difference −0.23, p 0.70 | none (low power, pre-registered) | 0.0077 | 0.963 | 0.0274 | 0.0013 |

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E056 zodiac labels as numbers (`ZODIAC_NUMBERS.md`) | NOT NUMBERS: positional identity 0.07% (p 0.91) vs planted numbers 48%; 245 types in 292 labels | sub-hypothesis NUMBERS × 1/10: 0.20 → 0.024 | 0.0077 | 0.963 | 0.0274 | 0.0013 |

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E057 per-word repeat individuality (`WORD_REPEAT_INDIVIDUALITY.md`) | VOID: the eligibility rule left too few words (Voynich 26; 4 of 5 languages unmeasurable). Unscored hint: Indonesian z +5.1, Voynich z +0.4 | none | 0.0077 | 0.963 | 0.0274 | 0.0013 |

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-24 | E058 per-word repeat individuality, v2 (`WORD_REPEAT_INDIVIDUALITY.md`) | VOID: only Indonesian of 5 references separates from the generator. Unscored: Voynich z −1.1 (family-like, like the generator), Indonesian +4.8 | none | 0.0077 | 0.963 | 0.0274 | 0.0013 |

**Unscored caution after E058.** On the one measure the forum proposed as generator-proof, Voynich's words behave
like their families: generator-like, not vocabulary-like. The reference set lacked power, so this is not scored. It
stays recorded as a lean towards M, alongside the weakened C21.

**Deviation (2026-10-24, end of session).** The bulk download of pharma-section canvases (for E055 preparation) also
fetched two canvases that contain the LOCKED leaf f102: `f101v_part_and_102r.jpg` and `f102v_part.jpg`. They were
never viewed or used, and were deleted before the session's data was moved into the repo. Future downloads must
exclude canvases whose label mentions 102.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E059 clean-up round (`CLEANUP_ROUND.md`) | Controls 4/4 PASS. d±: scribe 0.0% once line position (1.5%) and previous -y (1.9%) are in the model. q±: JUNCTION FORM (previous -y 7.5%, line 2.4%, location 0.1%). r/l location not reproduced (0.5%). e/ee MIXED at glyph level (t 0.37). Same-sheet pages alike (z +6.9 words, +6.9 glyphs), next page not (z +1.3). Label echo equal on own page (+4.2) and neighbouring pages (+3.4 to +4.5): SESSION ECHO | none (measurement, pre-registered) | 0.0077 | 0.963 | 0.0274 | 0.0013 |

**Facts corrected by E059.**
- **C18 withdrawn.** d± is not a scribe habit. It follows line position and whether the previous word ends in -y.
- **C19 replaced.** q± is a junction form: q- appears mainly after a word ending in -y. Location adds nothing. r/l's
  location dependence is too small to count (0.5%). "q as a meaning-carrier" is dropped.
- **C15 restated:** e and ee are one sign at word level only; what follows them differs at glyph level (eee differs from
  e more than r from l).
- **C7 restated:** words cluster **by sheet** (bifolio), not by reading order. Pages written on the same piece of vellum
  share vocabulary and glyph habits; the next page in reading order does not. This is a writing-process fact.
- **C23 restated:** labels echo the vocabulary of their neighbourhood (own page +4.2 points over frequency-matched words,
  other leaf of the sheet +3.6, adjacent page +4.5, random same-section page +2.2), not their own page in particular
  (own vs other leaf p 0.33). Pharma labels show the least (6.5% vs 5.7%).
- **C24 (new):** same-sheet pages are more alike than other pages of the same quire, scribe and section: words
  +0.069 cosine (7 of 9 quires), glyph bigrams +0.042 (9 of 9). Every page-level test must control for sheet.

**Reading.** Nothing moves, because C7 and C23 were never scored. But both had been leaning facts for L, and both are
now facts about how the book was written that a sheet-wise generator would also produce. The lower end of L's honest
range (0.60) is the more defensible reading.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E060 ingredient link (`INGREDIENT_LINK.md`) | VOID: Culpeper power control 0/20 (its first 10,000 Directions words are preamble; the names do recur in the full section, 98.7% vs 88%). Generator control 0/10 PASS. Unscored: 64 of 90 pharma label types occur in the recipes (71.1%) vs 68.2% for frequency-matched pharma-page words, p 0.24 | none | 0.0077 | 0.963 | 0.0274 | 0.0013 |

**Unscored observation after E060.** Pharma labels appear in the recipe section exactly as often as other words of
their frequency from the same pages. If they name ingredients, the recipes do not use them more than chance. The
test could not show its own power, so this is a lean, not a score.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E061 stems versus padding (`STEM_STREAM.md`) | VOID: the padding controls could not pass the pre-registered rule (languages too spread for a 3-sd bar); Caesar control passed. Unscored: Voynich stem stream is inside the language range (2,228 stems, 892 cover 95%, 55% hapax) and 6–8 sd from padding ciphers and the generator | none | 0.0077 | 0.963 | 0.0274 | 0.0013 |

**Unscored observation after E061.** The stems are not a small code alphabet: removing the endings leaves a language-
sized, language-shaped stem vocabulary. Endings do account for more of the word variety than in any language
(collapse 0.37 vs ≥ 0.48), consistent with C14, but they are not nulls. The step-3 attack is built on words.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E062 verbose cipher with one table per scribe (`SCRIBE_TABLES.md`) | CLASS FAILS: best set (German) fails 8 of 13 (Latin 9, Hebrew 10, Turkish 11). Per-scribe tables fix persistence, coverage and the Zipf head, but repeats stay at 0.9× chance against Voynich's 2.6×, vocabulary overshoots (7,580 vs 6,077) with too few one-offs, topic clustering 0.24 vs 0.39 | **C × 1/3** | 0.0078 | 0.9815 | 0.0093 | 0.0013 |

**After E062.** The last open verbose-cipher class (E020) fails on the same facts as every letter cipher since E016:
back-to-back repeats and the rare-word tail. Sensitivity from the range edges (L 0.60, M 0.25, C 0.13): C 0.052,
L 0.70, M 0.29; the ranking holds. C's honest range is about 0.01–0.05. What remains for C is a word-level system over
a doubling plaintext, or a mixed system with deliberate repetition.

**Observation (f57v, f66r):** the two key-like pages share a sign set the running text barely uses (four rare signs,
x, v) and omit its commonest glyphs. They are not an alphabet of the text.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E063 wide validated attack, 49 languages, Voynich A and B (`WIDE_ATTACK.md`) | NO CLAIM. 49/49 validated (both planted cracks 0.97–1.00 accuracy, 0 false claims on 588 controls). Voynich A 0.09–0.44 below threshold (median 0.26), B 0.09–0.46 (median 0.23); at or below pseudo-Voynich controls everywhere except Yapese A (+0.007) and Arabic B (+0.10, still 0.10 under T). engWycliffe untested | **L × 0.94, C × 0.96** (absence rule, "other European and unlisted" 0.27 of L-alpha-known, 0.8 covered; C substitution share 0.05) | 0.0083 | 0.9808 | 0.0095 | 0.0014 |

**After E063.** Sixty languages plus abbreviated Latin have now been searched in the VOY23 class with a validated
attack. L-alpha-known (prior 0.35 of L) retains about 0.07 of L's original mass: the m = 0.2 miss allowance plus
languages with no text on disk. Sensitivity: m = 0.1 gives L 0.9807; from the range edges (L 0.60, M 0.25, C 0.13)
the posterior is L 0.59, M 0.26, C 0.13. The ranking does not move; the shape of L does. A real language written letter
by letter with word boundaries kept is now the least likely form of L. Arabic B's margin over its controls is recorded
as seen beforehand for the queued abjad test (CLAUDE.md §6.5).

**Campaign close (steps 1–3 run, 4–5 dropped with reasons in `SCRIBE_TABLES.md` and `WIDE_ATTACK.md`).** E061 VOID
(informative), E062 C × 1/3, E063 L × 0.94 and C × 0.96. Net: M 0.0077 → 0.0083, L 0.963 → 0.9808, C 0.0274 → 0.0095.

**Correction (2026-10-25, before E064): tokenizer defect in the Bible loaders.** `e030.tokens` and `e042.words` split
words at combining marks, so Tamil, Malayalam, Assamese, Panjabi and Devanagari texts (seven of the E051 languages)
were measured as single-letter fragments (Tamil 1.72 M "words" for 0.43 M real ones). Affected: **E051 Part 1** (both
"matches", Tamil and Assamese, and the next five highest AS values are the seven fragmented languages; the withdrawal of
the E045 caution rests on them and is suspended until E064 Part C re-measures), E057/E058 (fragment references, VOID
anyway), E061 (Tamil's spread contributed to VOID), E063 (seven languages attacked as fragment streams: validated and no
claim, but not a test of the real language; the 0.8 coverage assumption absorbs it), E031's PG Telugu row (not
decisive). Unaffected: E030's primary languages, Hebrew, Arabic, all Latin-script results (apostrophes aside). Numbers in
earlier reports are left as written; E064 re-measures with a fixed tokenizer.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E064 re-audit of E030–E032 and E051 re-measurement (`EARLY_AUDIT.md`) | A: 0 of 30 fresh languages do both (max R 1.07 Assamese, max NR 1.52 Oromo) → E031 WITHDRAWN. B: five-scribe generator fails 7/13 (vocabulary 3,948 vs 6,077; one-offs 0.53 vs 0.68; Zipf −0.82 vs −0.65; persistence 0.49 vs 0.26; concentration 0.51 vs 0.29) → E032 stands. C: with correct words 0 of 30 reach AS 0.85 (Tamil 1.01 → 0.10, Assamese 0.87 → 0.75, Malayalam 0.76 → 0.02); BF(M:L) 2.8, no factor; **E045 caution reinstated** | **L × 1/3** (E031 withdrawn) | 0.024 | 0.9445 | 0.0274 | 0.004 |

**After E064.** The early chain E030 → E031 → E032 has lost one link. **Sensitivity: from the range edges (M 0.25,
L 0.60, C 0.13, O 0.02) the posterior is M 0.42, L 0.33, C 0.22, O 0.03, so M leads.** The M-versus-L ranking depends
on the starting point inside the agreed ranges, as it did after E030. L's honest range is now about 0.33–0.94; M about
0.02–0.42. The E051 entry's "Correction" paragraph (caution withdrawn) is itself corrected: the two fresh matches were
tokenizer fragments; with words, no ordinary prose among about 120 texts reaches Voynich's back-to-back level, and the
caution that C21 leans towards M stands again. E030's L × 3 stands (Indonesian and Malay reach R ≥ 1.5; none of the 30
fresh languages does). "Does both" (E031) is a drill-text property across 183 texts, a lead about genre, not language.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E065 syllable route go/no-go (`SYLLABLE_GONOGO.md`) | NO GO. Half 1: Voynich final-group classes E95 = 25 (bar 50); 9 reliable languages have 284–481 final syllables, 68–154 with codas dropped (nearest Turkish CV 68); Italian and Greek failed the syllabifier gate (untested, would fail). Half 2: syllable streams 826–1,499 types, 18–31% one-offs, vs Voynich 6,077 / 68%; Vietnamese reference 1,500 / 24% | **L × 0.921** (absence rule on L-syll: share 0.20, coverage 0.49, m 0.2) | 0.0259 | 0.9401 | 0.0296 | 0.0043 |

**After E065.** Forms of L (shares of L): lost or unrecorded language 0.33, syllable signs 0.20, abbreviation 0.18,
mixed/other 0.16, letter by letter 0.14. The lead within L has passed to the form that cannot be read with any
dictionary, only tested on grammar shape. From the range edges M 0.43, L 0.31, C 0.22, O 0.03.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E066 word-specific self-repetition, v3 with correct words and 60 languages (`WORD_INDIVIDUALITY_V3.md`) | VALID (Tagalog +13.8, Indonesian +4.8, Oromo +4.4, Lingala +4.1 separate from the generator; 15 of 60 measurable). **Voynich FAMILY-LEVEL:** z −1.2 (112 words, 188 / 189 repeats) vs generator median +0.55, max +2.0 | **M × 3** (pre-registered). Empirical ratio only 1.4: 11 of 15 measurable languages are also family-level | 0.0739 | 0.8939 | 0.0281 | 0.0041 |

**After E066.** First scored result that M wins. From the range edges: M 0.70, L 0.17, C 0.12. With the empirical ratio
(× 1.4) instead of the pre-registered × 3: M 0.035, L 0.93. Either way M is now above C for the first time since E032. The
per-word-repeat family is closed (E057, E058, E066). What M still lacks is a procedure that makes Voynich's vocabulary
(E064 Part B); what L still lacks is any text, in any language or genre, that repeats like Voynich without a doubling
grammar, and the doubling languages (Indonesian, Tagalog) show word personalities Voynich does not.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E067 human gibberish vocabulary growth at 150-token windows (`GIBBERISH_VOCABULARY.md`) | GIBBERISH LIKE VOYNICH: 36 writers T 115.2, H 0.67 vs Voynich 112.1 ± 11.0, 0.62 (d_T +0.28, d_H +0.59); 60 Bibles 94.5 / 0.47 (d −1.60), generator 93.8 / 0.46 (d −1.67). Caveats: 14 of 60 languages (Hebrew, Tamil, Arabic, Turkish…) are as rich; writers scatter 71–148; 150 tokens only | **M × 3** | 0.1932 | 0.7788 | 0.0245 | 0.0036 |

**After E067.** Two scored wins for M in a row (E066, E067), both weak by design. At the point values L 0.78, M 0.19;
from the range edges M 0.87, L 0.07. M's remaining gaps: book-scale vocabulary (no human sample is long enough), and
the line-level facts never tested on human gibberish (near-copies, endings, h2, word length; AS was 0.66 in E045).
L's gap is unchanged: no non-doubling text repeats like Voynich, and doubling languages show word personalities Voynich
lacks. The honest headline: **a two-horse race, L ahead at our starting point, M ahead from the edges.**

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E068 human gibberish on the small-scale battery (`GIBBERISH_BATTERY.md`) | 5 diagnostic features; gibberish Voynich-like on 1 (near-copies NR 1.31 vs Voynich 1.23, languages 0.53), language-like on 4 (word-length spread 2.41 vs 1.71, H2 2.98 vs 1.98 bits, ending concentration 0.62 vs 0.93, back-to-back R 0.55 vs 1.28). Generator matches the four shape features and NR but not R | **M × 1/3** | 0.0739 | 0.8938 | 0.0281 | 0.0041 |

**After E068.** Human free gibberish supplies vocabulary (E067) and near-copies; the copy generator supplies rigid word
shapes, endings and near-copies; neither supplies exact repeats at Voynich's rate; neither supplies everything. M now
requires the conjunction "a disciplined invented word-system, used by a free human inventor who also doubles words".
From the range edges M 0.69, L 0.17. Arham's framing for the day: M is ruled down, not out; the work continues inside
L with M kept symmetric.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E069 word-partner persistence across halves (`WORD_PARTNERS.md`) | Gate passed (10/10 generator below language p10). Voynich ALL STAB 0.073: above every generator stretch (max 0.053), below the languages' 10th percentile (0.083); seed rule 9/10 INCONCLUSIVE. A-only 0.023 generator-like at its size; B-only 0.044 between. Only Polish, Slovak, Azerbaijani, Hebrew score as low | none | 0.0739 | 0.8939 | 0.0281 | 0.0041 |

**After E069.** Voynich's common words have weak but real partnerships that carry across the book: more than a copying
process, less than 56 of 60 languages, like languages whose commonest words are grammatical pieces. The first
grammar-shape test of the unrecorded-language form is a draw.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-25 | E070 content-word partner persistence, ranks 51–250 (`CONTENT_PARTNERS.md`; statistic amended before any real measurement) | Gate passed. Voynich ALL PSO 0.004 (15 of ~860 partner pairs persist; shuffled 13): below every language (min 0.018) and the generator median (0.027). A-only 0.009 vs its generator median 0.008 → safeguard fails by a hair; seed rule 9/10 INCONCLUSIVE | none (rule as written). Partner family closed | 0.0739 | 0.8939 | 0.0281 | 0.0041 |

**After E070 (unscored lean).** Voynich's content-like words have no partnerships that persist across the book, unlike
all 60 languages. With E066 and E069 this says individual Voynich words carry no persistent association, which is what
a meaningless process gives. The one alternative that must be tested before this is read against L: a **catalogue**
text (each entry its own vocabulary: a herbal, a pharmacopoeia) could also lack persistent content partners. Bibles
are the wrong comparison for that; Culpeper and the Gaskell & Bowern technical texts are the right one. Not yet tested.

**Descriptive, unscored (2026-10-26): label-class step 0, line position** (`LABEL_STEP0.md`). The o-tall-letter words
(659 types, 3,596 prose tokens) open lines half as often as frequency-matched words (0.056 vs band 0.094–0.148) and
paragraphs a third as often; they sit slightly late in the line (relative position 0.56 vs 0.47–0.52) and show no
neighbour lock. The 70 zodiac-label types in prose agree. Reading 1 of the label-class programme (list words, pointers)
is set aside: its main prediction (entry-initial position) fails. Readings 2 (names) and 3 (abbreviations) survive.

| Date | Test | Outcome | Bayes factors | M | L | C | O |
|---|---|---|---|---|---|---|---|
| 2026-10-26 | E071 label words as truncations of longer words (`LABEL_TRUNCATION.md`) | VALID: G&B abbreviated Pliny z +14 to +16 (3 windows), planted truncations z +12 to +21 (3 languages), 9 false-claim sets within ±1.7. Voynich: 95 o-gallows label words z +0.44 (general), +0.52 (class-internal); 280 label words z +0.04; 0/10 seeds above the bar. NOT ABBREVIATION-LIKE | within L only: **L-abbrev × 0.6** (absence rule, s 0.5, m 0.2). Forms of L: unattested 0.35, syll 0.21, abbrev 0.12, other 0.17, alpha-known 0.15 | 0.0739 | 0.8938 | 0.0281 | 0.0041 |

**After E071.** The label words are not shortened forms of longer words. Of the five readings of the label class, list
words (step 0), abbreviations (E071), quantities (E056, step 0) and category + identifier (same markers on plants and
figures) are weakened; title + name is the one left with an untested prediction, and it needs the zodiac images.
