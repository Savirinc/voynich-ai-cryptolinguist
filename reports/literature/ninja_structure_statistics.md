# voynich.ninja: text STRUCTURE and STATISTICS, mapped against our findings (C2 to C23)

Compiled 2026-10-24. Read-only research. Nothing was posted and I did not log in.

## How this was gathered, and its limits

- **What I read.** I read about 34 threads directly through WebFetch: 4418, 4343, 5644, 3107, 3021, 5710, 5373, 5384, 5864, 4361, 4346, 5357, 5336, 3153, 3640, 61, 4944, 1812, 3891, 3775, 148 (p7), 3356 (p8), 6112, 4230, 4389, 3890, 2111, 5861, 2357, 2808, 4779 and 2995. Several more are known only from search-engine snippets: 3344, 2790, 4205, 3431, 5309, 5765 and 5081.
- **Most replies were hidden.** The forum hides reply bodies from guests ("Register or login to view the content"). Normally only the opening post is readable, and some older threads (3640, 3891, 2808, 3890) show replies. So I could see rebuttals only in those few threads. Elsewhere I name who replied but cannot say what they argued. Snippet-only claims are marked **[snippet]**.
- **Fetch problems.** Direct curl to www.voynich.ninja hung after one request. WebFetch hit a session limit at the very end.

---

## 1. Word grammar and slot models

**1a. Mauro: "A family of grammars for Voynichese"**
https://voynich.ninja/thread-4418.html (Nov 2024, 15 pages; replies from MarcoP, nablator and ReneZ are hidden)
- Mauro proposes three grammars: BASIC, COMPACT and EXTENDED.
- **BASIC** covers 48.7 to 50.6% of word types.
- **COMPACT** is 3 to 6 times more efficient than BASIC. Efficiency = attested words ÷ all strings the grammar can generate.
- **EXTENDED** covers 88.45% of word types, or 92.79% once words with rare glyphs (g, v, ...) are excluded.
- He benchmarks against ThomasCoon, Zattera and Stolfi, and claims better efficiency than ThomasCoon and Zattera.
- *Relation:* **CONFIRMS C3/C5.** A small slot grammar covers about 90% of types, which is the rigidity we measure.
- *Lead:* The efficiency metric is the useful part. **Pre-register:** fit the same slot-grammar search to Hawaiian, Maori and pinyin (our C3 comparison languages), with equal grammar size. Then compare coverage and efficiency against Voynich A and B. If Voynich B beats every language on efficiency at equal coverage, that is a clean, quotable rigidity statistic.

**1b. Zattera's 12-slot sequence, and nablator's 10-slot variant**
https://voynich.ninja/thread-4230.html (nablator, Apr 2024); Zattera numbers from the search snippet for 4418/4230
- Per the forum, Zattera's "regular" words are 51% of word types. His SLOT MACHINE state-machine variant covers only 21.6%.
- Slots 7 to 11 share six glyphs with slots 0 to 2. This "wrap-around" means space-less text can be split several ways.
- nablator's unambiguous 10-slot order: qo | k,t,p,f | ch,Sh | cKh,cTh,cPh,cFh | e,ee,eee | o,a | i,ii,iii | d,l,r,s | m,n | y.
- *Relation:* **CONFIRMS C3.** Note that nablator puts e/ee/eee in one slot (our C15) and k/t/p/f in one slot (our C16).
- *Lead:* The wrap-around overlap is exactly what a verbose or syllabic chunking would produce. **Test:** delete all spaces in held-out leaves, segment with the slot grammar, and measure how often the original spaces are recovered. High recovery means spaces are predictable from glyph content, which would make "words" a slot-cycle artefact.

**1c. Stolfi's core-mantle-crust model**
https://voynich.ninja/thread-3153.html (-JKP-, 2020; content hidden); snippets from 3613 and 5384
- Five optional layers: the core is gallows, the mantle is benches and e-runs, the crust is the rest.
- **[snippet]** One user's "cipher wheels" built on it cover about 93% of words.
- Stolfi is still active on the forum (he replies in 5373, 5384 and 6112).
- *Relation:* **CONFIRMS C3/C5.**

**1d. davidjackson: "A brief summary of Voynichese spelling and grammar"**
https://voynich.ninja/thread-4779.html (curated, 2017 to 2021)
- **q** is followed by o about 90% of the time. Most q-words also occur without the q. No label uses q.
- **i** is followed by i or n about 90% of the time.
- Swappable pairs: ch/sh, t/k, l/r, y/o, o/a, l/m.
- **Asymmetric word pair:** "or" occurs 366 times and "aiin" 470 times, but "or aiin" is far more common than "aiin or".
- No common line-opening word: "ychor" starts 16 lines.
- Timm found 35 triple repetitions (X X X).
- *Relation:* The swappable pairs **CONFIRM C12.** The pair asymmetry **EXTENDS the word-order finding (line 12 of our findings).**

**1e. vosreth: "What are Voynichese words?" and "Many-to-one"**
https://voynich.ninja/thread-5336.html and https://voynich.ninja/thread-5357.html (Dec 2025 to Feb 2026; 38,525 tokens)
- **q:** 99% word-initial, followed by o 97% of the time.
- **k and t:** co-occur in under 2% of words; when both appear, t precedes k (2:1 in one post, 3:1 in the other).
- **e-runs after ch/sh:** Currier A is e 57%, ee 34%, eee 9%. Currier B is e 65%, ee 27%, eee 10%.
- **Following glyph varies with run length:** P(next = s) is 1% after e, 4% after ee and 13% after eee. Longer runs shift toward following k/t rather than ch/sh.
- **ch:sh ratio:** 2.75 in A, 2.12 in B. sh is word-initial 71% of the time, ch 57%.
- **Other glyphs:** m is 95% word-final; y is 93% word-final; a is never final.
- **Across word boundaries:** after a y-final word the next word starts with q 27% of the time; after an l-final word, with ch/sh 33%.
- **s and q by text type:** s is enriched 2× line-initially. Labels have q 1% and s 16%; paragraph text has q 16% and s 7%.
- He argues the Naibbe cipher fails on the cross-word effects.
- *Relation:*
  - The e/ee/eee result **partly CONTRADICTS C15** (e = ee as one sign). If ee were just a spelling of e, its left and right neighbours would match those of e. Here they differ systematically (eee → s is 13× e → s).
  - k/t co-occurring under 2% **CONFIRMS C16** (same slot), but see 3b.
  - The q-after-y rate is **NEW.**
- *Lead (strong):* **Pre-register a neighbour-distribution equality test for e vs ee vs eee**, and likewise in vs iin and ain vs aiin: compare left and right context distributions with a permutation test. C15 predicts no difference beyond chance. Also condition on the preceding glyph: ch/sh vs k/t.

---

## 2. Line-position and paragraph effects

Our findings never mention line position. This is the forum's richest quantitative area, and almost all of it is **NEW** to us.

**2a. tavie: Voynich Day 2024 "Line Patterns" (Herbal A scribe 1, Balneo scribe 2, Stars scribe 3)**
https://voynich.ninja/thread-4343.html
- **Line-initial ch is suppressed.** ch is 24% of mid-line word-initials, so about 300 line-initial ch would be expected in Herbal A; only 64 occur.
- Line-initial words favour y, d and s. Scribe 1 favours o and q; scribes 2 and 3 avoid o.
- Line-final words avoid final y, favour final m, and avoid initial q/ch/sh. Scribe 1 strongly favours "da-" at line end.
- The top row of a paragraph favours initial o and final y, and avoids final n.
- **"Vertical impact":** in Herbal A about 40 o-over-o line-initial pairs (consecutive lines) are expected, but **1** occurs (f10r). o-over-q has a surplus of about 38, while q-over-o has only about 8.
- **[snippet]** Some rare words are tied to one position: "dsheey" is line-initial in 7 of 8 occurrences, "dalam" line-final in 6 of 7.
- *Relation:* **NEW.** This is a dependency between lines, not between words.
- *Lead:* **Pre-register a vertical-impact test on held-out leaves.** Count the first glyphs of vertically adjacent lines against a within-page shuffle of line order. Predictions: o-o is depleted (observed/expected < 0.2) and o→q is enriched with a directional asymmetry. A meaningful-language text is very unlikely to do this; a copy-from-line-above generator might.

**2b. JoJo_Jost: "The first glyph of every line"**
https://voynich.ninja/thread-5644.html (Apr 2026)
- The first token of a line is longer than other tokens: average length 4.91 vs 4.49.
- Its internal bigrams are "anomalous" (negative PMI) 41.5% of the time vs 28.2% elsewhere.
- Removing the first unit cuts the anomaly rate by 20 points at position 1, but by only 7 to 8 points elsewhere. So the effect sits in the first glyph alone.
- Seven units make up 85.5% of line-initial glyphs. p is 8.5× over-represented and s 5.7×.
- The opening glyph varies by section (chi-square): o in Astro, q in Herbal and Balneo, p in Recipes.
- 72% of page-first lines begin with a gallows.
- *Relation:* **NEW.** It also affects C2/C3: line-initial glyphs are atypical, which inflates the h2 estimate a little. Our h2 values should be recomputed without them.
- *Lead:* **Strip the first glyph of each line, then re-measure h2, word-length distribution and hapax rate.** Pre-register that the first token's anomaly rate falls to the mid-line level. If it does, line-initial glyphs are an extra line-level marker (a calligraphic convention, a cipher "null", or a clitic). They should then be excluded from every language comparison.

**2c. Patrick Feaster: "Rightward and Downward" (replicated by MarcoP, critiqued by Emma May Smith)**
https://voynich.ninja/thread-3640.html; also https://voynich.ninja/thread-5864.html (JoeyB's 2026 compilation)
- **o vs qo:** the o/qo ratio rises steeply in the second half of a line. MarcoP reproduced this in all three single-scribe sections; Q13 is most extreme, Herbal A least.
- **Glyph drift along the line (Currier A, lines cut into 5 parts):**
  - ch falls 804 → 672
  - Sh falls 312 → 149
  - d rises 287 → 771
  - s rises 92 → 204
- Currier A and B behave quite differently in this respect.
- Within a line, sh drifts to ch, qo to o, and k to t (**k→t rightward**).
- **[snippet]** In Currier B, about 30% of daiin tokens are line-first, against an 11.5% baseline. For scribe 3, line-initial daiin depends on recto vs verso, and the effect vanishes when recto/verso labels are scrambled.
- **Rebuttal (visible):** Emma May Smith argued that average line length differs by word and by section, so "rightwardness" scores may be partly a line-length artefact. She also asked for absolute effects (e.g. final m) to be separated from gradual trends. Feaster agreed the two kinds differ; the issue was not settled.
- *Relation:* **EXTENDS / CHALLENGES C16, C17 and C19:**
  - **C17** (d-forms are a scribe habit: scribe 1 about 23%, scribes 2 and 5 about 56 to 59%). d nearly triples from line start to line end in Currier A. If scribes differ in line length or layout, part of our "scribe" effect could be line position.
  - **C16** (t ≈ k). If k turns into t rightward, t and k may be positional variants, which would explain why they behave as nearly one sign.
  - **C19** (q- depends on location in the book). q- also depends on location within the line.
- *Lead (high priority):* **Fit a logistic model for each binary alternation in C12: e/ee, r/l, d±, q±, t/k.** Predictors: line-position bin, paragraph line index, scribe, section and Currier language, all fitted jointly. Pre-register which factor dominates each alternation. This directly tests whether C17's scribe effect survives a line-position control (Emma's confound) and whether t/k is positionally conditioned.

**2d. Stolfi on m and g (quoted in Koen G's thread)**
https://voynich.ninja/thread-4389.html
- m is "inordinately common" at line ends and before figure interruptions.
- 862 of 950 m-tokens (91%) follow a or o. Only 56 (5.8%) follow ai/aii.
- g: 27 tokens, 24 word-final.
- Hypothesis: m abbreviates -iin when space is tight.
- *Relation:* **NEW.** It is a concrete case of a positional allograph.
- *Lead:* **Test complementary distribution.** P(-am | line-final) / P(-am | mid-line) should mirror P(-aiin | mid-line) / P(-aiin | line-final). If m ≈ iin, merging them should leave h2 and the ending inventory (C5) almost unchanged and make line-final words look like mid-line words.

**2e. Smaller line and paragraph items**
- **sh and the paragraph's first line.** https://voynich.ninja/thread-4205.html **[snippet]** sh-initial words show a general upward trend toward the paragraph's literal first line, while ch-words not preceded by p peak on line 1 itself. The effect is weaker in Balneo.
- **chd/shd near line ends.** https://voynich.ninja/thread-3021.html (nickpelling) Herbal A chd/shd words sit at line ends or just before drawings. Counts are small.
- **Line-length words.** Vogt (2012), cited in 5864: the first word of a line is longer and the second word shorter.
- **Generators ignore line position.** https://voynich.ninja/thread-5864.html JoeyB argues that generator theories must explain all of these effects together. **[snippet, thread-5081]** Critics say Naibbe is position-agnostic at line level and cannot reproduce them; its author concedes this.
- *Lead:* **A discriminator for our generator comparisons (C9/C21).** Run the line-position battery (2a to 2d) on the Timm-Schinner generator output. Its source chooser is position-aware: it reuses the same writing position with probability 0.28, and paragraph-initial lines draw from earlier paragraph-initial lines **[snippet, 2790]**. Naibbe-style output is position-free. Voynich effect sizes then become a pre-registered target that natural languages, Naibbe and Timm-Schinner each either hit or miss.

---

## 3. Glyph alternations, allographs and positional variants

**3a. Koen G: "Why not positional variation?"**
https://voynich.ninja/thread-4361.html (Sep 2024; replies from ReneZ, RadioFM and Rafal are hidden)
- Koen proposes several glyphs as positional variants of others:
  - n = the final glyph of an i-series
  - s = the final glyph of a c-series (s and n as word-final flourishes)
  - q = the form y takes before o
  - a = the first glyph of a minim series not preceded by o
- **[snippet]** Words differing only in iin vs in "behave quite similarly".
- *Relation:* The iin ≈ in point **CONFIRMS the C15 logic.** The y → q idea is **NEW** and meshes with vosreth's figures: y is 93% word-final, q 99% word-initial, and q follows y-final words 27% of the time.
- *Lead:* **Test whether q- is conditioned by the previous word's ending.** Compute P(q- | previous word ends in -y) vs P(q- | other endings), within lines only. Compare to a within-line shuffle. If the dependence is strong, the q± alternation in C12 is partly a sandhi effect across the boundary rather than a property of the word. That would also fit C19: q- varies by location because ending mixes vary by section.

**3b. t/k and ch/sh beyond C16**
- Section-dependent k:t ratios (5357).
- k→t drift along the line (3640).
- k and t essentially never co-occur in a word (5336).
- ch:sh differs by Currier language (2.75 vs 2.12).
- sh is favoured near paragraph tops (4205). Davidsch claims sh-words are shorter than ch-words: https://voynich.ninja/thread-2995.html (poll only; content hidden).
- *Relation:* **EXTENDS C16** (t ≈ k). Treat t/k and ch/sh as possible position- or section-conditioned variants, not free variants.

**3c. Emma May Smith on glyphs across word breaks**
https://voynich.ninja/thread-2808.html (paper discussion; replies visible)
- The last glyph of one word and the first glyph of the next are not independent.
- nickpelling objected that this is Currier's old observation. ReneZ noted that Currier saw it only in the Biological pages.
- *Relation:* **EXTENDS C12/C21.**

---

## 4. Reduplication, near-repeats and self-citation

**4a. Rates**
- **MarcoP's reduplication plot (verified).** https://voynich.ninja/thread-61-page-9.html, post #81, 28-03-2021. The plot is the attachment `_europe.png` (aid 5413). It compares exact and quasi-reduplication in EVA Voynichese against European languages.
  - **Answer: Voynich has MORE back-to-back exact repeats than the European languages, by about 10×.**
  - MarcoP's words: *"Duplicates amount to almost 1% of Voynichese."* *"In actual European texts, they are about one order of magnitude rarer or more."* *"As you can see, the distance is abysmal."*
  - Exception: *"Vietnamese (VIE) shows that some Eastern languages are better fits for reduplication in the VMS"*, though not for quasi-reduplication.
  - The page text gives no exact per-language plotted values.
  - **[snippet]** Elsewhere, MarcoP showed that rewriting every Latin "ad" as "ad ad" yields about 1% reduplication, as in the VMS.
- MarcoP, https://voynich.ninja/thread-3107.html: near-duplicates differing by one character ("quasi-reduplication") are about twice as frequent as exact ones. The visible opening post only lists examples (French cookery) and proposes testing whether exact and near repeats are linked. **[snippet]** A later reply reports a correlation of about 0.82 to 0.85 between the perfect- and quasi-reduplication rates.
- *Our C21 lines up with this.* Only reduplicating languages (Indonesian, Tamil, Assamese) reach the Voynich rate; for MarcoP, Vietnamese.
- Bowern and Lindemann, via https://voynich.ninja/thread-3344.html **[snippet]**: P(repeat) is 0.84% in A and 0.94% in B. Their language corpus ranges from 0.02% to 4.8%, average 0.63%.
- Gaskell and Bowern found human gibberish varies widely and can match either natural language or Voynichese. A footnote says students could not keep language-like non-language going beyond about 100 words without local repetition.
- *Relation:* **CONFIRMS C9/C21**, and the near-repeat point **CONFIRMS C12.** The 0.02 to 4.8% corpus range is a warning: our "not avoided (ratio 1.0)" metric is more robust than raw rates, so we should keep reporting it.
- *Lead:* **The exact vs quasi link (MarcoP).** Pre-register that the quasi-repeat rate is elevated by the same factor where exact repeats are elevated: by section, by scribe, and by position in the line. Copying or self-citation predicts the two co-vary. Grammatical reduplication predicts exact repeats concentrate on a closed word class (daiin is about 6.6% of all repeats) while quasi-repeats do not.

**4b. MarcoP: alternating patterns**
https://voynich.ninja/thread-2357.html
- Patterns tested: X Y X Z, chiasmus X Y Y X, and X Y X Y.
- qokain has the most X Y X Z matches (9); in Quire 13, observed matches are almost double the expected number.
- Six chiasmus and six X Y X Y cases in the manuscript.
- In comparison texts, "e"/"and" (Dante, KJV Genesis) match slightly below random, while Latin "et" matches above.
- *Relation:* **EXTENDS C9** (within-line recurrence at gap 2 and beyond).
- *Lead:* Extend our back-to-back repeat ratio to gaps 2 and 3 and test for a monotone decay. A copy-from-recent-text mechanism predicts a smooth decay; grammatical reduplication predicts a spike at gap 1 only.

**4c. Timm-Schinner self-citation**
- Thread 2790, thread 4765, and https://voynich.ninja/thread-1812.html (DonaldFisk's separate state-table generator claims 90% reproduction; replies hidden).
- **[snippet]** A 2026 arXiv port (2608.17096; I did not verify it) reports the mechanism **saturates at 57 to 60% singletons** whatever the settings, and that seeds vary widely.
- *Relation:* If that holds, our **C4 (~68% hapax)** is above what the generator can reach. That is a possible quantitative strike against it. Verify before citing.
- **Vuk88's "double words" thread** (https://voynich.ninja/thread-5861.html) claims doubles peak next to gaps in the codex. The author is banned and the folio count is internally inconsistent; low value.

---

## 5. Currier A/B, scribes, and what separates them

**5a. Dunsel: "The oddities of the bigram ed" (parts 1 to 3)**
https://voynich.ninja/thread-5373.html and https://voynich.ninja/thread-5384.html (Feb 2026; Stolfi, ReneZ, oshfdk and Koen replied, hidden)
- Splits pages into "0ED" (A-like, 104 pages) and "ED+" (B-like, 121 pages).
- **Out-of-vocabulary (OOV) rates:**
  - Trained on 0ED and tested on ED+: 40.7% of tokens are OOV.
  - Trained on ED+ and tested on 0ED: 19.5%.
  - About 82% of ED+ OOV tokens become 0ED words with one substitution or deletion, and 99% within three edits.
  - ED+-only words fall within two edits of 0ED 93.7% of the time, against about 69% for Latin (Caesar) and 66% for English (Dracula).
- **Bigram densities:**
  - "ho" density: 0.264 (0ED) vs 0.056 (ED+).
  - "ed" density: 0.0007 (0ED) vs 0.18 (ED+).
- The author got a page classifier formula from ChatGPT; it is unverified.
- *Relation:* **EXTENDS C20** (same grammar shape, different favourite words). It suggests B vocabulary is A vocabulary with systematic edits.

**5b. npcompl33t: two rules linking Herbal A to Herbal B**
https://voynich.ninja/thread-6112.html (Sep 2026)
- Rule 1: chy → edy (e.g. qokchy → qokedy).
- Rule 2: chy → chdy (e.g. qotchy → qotchdy).
- Evidence for Rule 1: 17 A→B pairs, frequency ranks matched with Spearman ρ = 0.758, permutation p = 0.0004, Holm-adjusted p = 0.0047.
- chedy, shedy, cheedy and sheedy make up about 40% of the "missing" token mass.
- *Relation:* **EXTENDS C20.** Notably, Rule 2 inserts d, so it touches **C17** (d-forms as a scribe habit). Our scribe-1 vs scribes-2/5 d-gap may be the same A→B respelling.
- *Lead (strong):* **Pre-register: in held-out A and B leaves, frequency-matched word pairs related by chy→edy or chy→chdy show rank correlation above that of random one-edit pairs.** Then re-run C17 with these word pairs merged. If the scribe gap in d-forms shrinks, C17 is really the A→B rule.

**5c. Labyrinthinesecurity: "Currier A/B split is not what we thought it was!"**
https://voynich.ninja/thread-5710.html (May 2026; unreviewed; replies hidden)
- **The switch:** the vowel after ch/sh (o vs e) defines a folio-level two-state switch. A two-state mixture model fits far better than one state (AIC improvement 2,549); 195 of 197 folios are assigned unambiguously.
- **Agreement with plant drawings (101 Herbal folios, Koen's morphometrics):** the switch agrees 96% (κ = 0.87). Currier's A/B labels agree only 78% (κ = 0.106).
- **Where switch and Currier disagree:** 27 folios; 18 have morphometric data, and in all 18 the drawings side with the switch.
- **Named examples:** f31r, f34v, f39r, f43r and f46r are traditionally A but E-dominant. f87r, f90r and f93v are traditionally B but O-dominant.
- *Relation:* **CHALLENGES the labelling behind C17, C19 and C20.**
- *Lead:* **Cheap re-labelling test.** Recompute our A/B-split statistics (C3's B rigidity, the C20 Zipf-head mixing, C17's d-forms) under both Currier labels and the switch labels. Pre-register that the switch sharpens the differences (larger effect size, fewer mixed folios).

**5d. Scribes: Torsten's critique of Davis**
https://voynich.ninja/thread-3890.html
- Davis's five scribes rest on letter shapes (EVA k crossbar, iin/in) uploaded from only about 44 pages to Archetype.
- Scribe 4 (the zodiac pages) coincides with Zandbergen's observation that qo is nearly absent from the zodiac and rosette pages.
- Davis replied (visibly) that her assignments rest on "tendencies".
- *Relation:* **Relevant to C17/C19.** C19 says q- depends on book location, not scribe; for scribe 4 the two cannot be separated, because scribe and location coincide.
- *Lead:* Report C17/C19 on the folios where scribe and section are not confounded, and state how many folios our scribe labels depend on.
- **[snippet, thread-120 and 1523]** Torsten and ReneZ show A and B grade into each other through intermediate pages (chol and chor fall; chedy rises). **CONFIRMS C20.**
- **[snippet, thread-3431]** One grammar test finds invalid-word rates of 37.95% in A and 27.99% in B. **CONFIRMS C3** (B more rigid).

---

## 6. Entropy and verbose-cipher arguments

- **Koen G, "An Essay on Entropy"** (https://voynich.ninja/thread-3775.html):
  - Voynich h2 is about 2, and Quire 13 about 1.8. Medieval texts are above 2.8, nearly always above 3.
  - Merging benches (ch) and in-clusters raises h2 but leaves it far below normal.
  - Rewriting frequent n-grams (dy, etc.) as single signs gives near-normal h2 (**3.01** in a bigram set cited in https://voynich.ninja/thread-3356-page-8.html), but makes words too short.
  - Koen's own takeaway: a valid solution must change entropy density without inventing information.
  - **[snippet, thread-148]** A related thread asks how to recombine glyphs to raise h2. Anton (visible) notes that a "base shape + tail" decomposition makes most words even-length.
- *Relation:* **CONFIRMS C2/C3** exactly. Our framing of C3 ("inside simple-syllable languages only when ch, sh, iin, ee, qo, dy are units") is the same trade-off.
- *Lead:* **Add the word-length check Koen raises.** After our C3 merges, compare the mean and the full distribution of word length in units against Hawaiian, Maori and pinyin syllable counts per word. Pre-register that Voynich lands inside the syllable-language range on h2 **and** length together. If length falls outside, the syllabic reading of C3 is weakened.

---

## 7. Word order and syntax measurements

- **Emma May Smith: ending-to-ending transitions in Currier B** (https://voynich.ninja/thread-4346.html):
  - y is the top follower of almost every ending (0.31 to 0.49); y → y is 0.49.
  - edy → edy is 0.29 and ey → ey is 0.19: each word ending tends to recur in the next word.
  - in and m prefer ey; l and d prefer edy.
  - ol/al behave like l, or/ar like r, and ain/iin like in.
- *Relation:* **NEW / EXTENDS C5 and C9.** C5 says the stem barely predicts the ending. Emma shows the **previous word's ending does** predict it. That is agreement-like, or "rhyme"-like (copying).
- *Lead (strong, cheap):* **Pre-register: within lines, the mutual information between consecutive words' endings is above a within-line shuffle, and above Latin, Turkish and Swahili (which have real agreement) once normalised by ending entropy.** Also compare against the Timm generator. Copy-based generators should produce ending persistence; agreement languages produce it only for specific pairs (determiner + noun), not as blanket self-attraction.
- **Caruana (Malta) word-pair AB:BA asymmetry**, via https://voynich.ninja/thread-3891.html:
  - Voynich shows about a 2:1 AB:BA asymmetry; randomised text scores about half as much.
  - **Visible rebuttals:** RenegadeHealer says no real pseudotext generator was tested, and generators may also give ratios above 1. nablator says the result depends on thresholds and recommends Fincher's threshold-free Word Pair Permutation Analysis instead.
  - **Relation:** ties to our "word order carries weak information" finding.
  - **Lead:** run a threshold-free AB/BA asymmetry measure on Voynich, our languages, hymns/Psalms, and the Timm generator. This is a good falsifiable discriminator for the "like hymns or like the generator" ambiguity.

---

## TOP 5 most important items for us

1. **Line position is a large, unmodelled factor, and it may confound C16, C17 and C19.**
   - Sources: Feaster and MarcoP (3640), tavie (4343), JoJo_Jost (5644).
   - The effects: d nearly triples from line start to line end in Currier A, qo turns into o and k into t rightward, line-initial ch is 4–5× depleted, and p is 8.5× over-represented line-initially.
   - **Action:** one pre-registered joint logistic model per C12 alternation, with line position, paragraph line, scribe, section and Currier language as predictors. Check whether C17's "scribe habit" for d survives.
2. **e vs ee vs eee neighbours differ, which threatens C15.** vosreth (5336, 5357): P(next = s) is 1%, 4% and 13% after e, ee and eee, and the preceding glyph shifts as runs lengthen. **Action:** a pre-registered left/right context-equality test for e/ee/eee and in/iin, with a permutation null.
3. **Endings attract endings across word boundaries.** Emma May Smith (4346): y → y 0.49, edy → edy 0.29. C5 says the stem doesn't predict the ending, but the previous word's ending does. **Action:** a within-line ending mutual-information test against shuffles, agreement languages and the Timm generator. It separates agreement grammar from copying.
4. **A→B may be a systematic respelling, and the A/B labels themselves may be off.**
   - Sources: Dunsel (5373: about 82% of B-only tokens are one edit from A), npcompl33t (6112: chy → edy/chdy, ρ = 0.76), Labyrinthinesecurity (5710: an o/e folio switch matches the drawings with κ = 0.87, against Currier's κ = 0.11).
   - **Action:** re-run C17 and C20 under the switch labels and with the chy-rule pairs merged.
5. **q- as a boundary (sandhi) effect, and line-position effects as a generator discriminator.**
   - Sources: Koen (4361, q as the form y takes before o) and vosreth (q follows y-final words 27% of the time).
   - **Action:** test P(q- | previous word ends in -y) against a within-line shuffle (this would explain the q± part of C12 and C19).
   - **Action:** run the full line-position battery on Timm-Schinner and Naibbe-style output. Neither natural language nor a position-free cipher is expected to reproduce tavie's vertical o-o depletion (1 observed vs about 40 expected).
