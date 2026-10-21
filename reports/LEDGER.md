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
