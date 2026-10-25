# E059 (clean-up round): line position and writing session as confounds — results

Pre-registration `reports/E059_PREREG.md` (sha256 ca018b07…da0c6, commit 9f89cab). Script
`experiments/e059_cleanup_round.py` (sha256 c0a129b8…1ff1). Results: `experiments/results/e059.json`,
`e059_run.log`. Runtime 225 s. Measurement round; **no ledger factor** (pre-registered). No permutation p fell in the
borderline band, so no seed replicate was needed.

**Part A1 controls passed (4 of 4):** each planted habit (line end, scribe, quire, previous -y) was found by its own
factor, and no other factor was marked PRESENT. Part A1 is VALID.

## Summary in one table
| Fact | Before | After E059 |
|---|---|---|
| C18: d± is a scribe habit | scribe explains 13% (E039) | **Withdrawn.** With line position and the previous word in the model, the scribe explains nothing (0.01%). d-forms follow line position (1.5%) and whether the previous word ends in -y (1.9%). |
| C19: q± follows location | location, not scribe (E039) | **Withdrawn, replaced:** **q is a junction form.** Whether a word takes q is explained mainly by the previous word ending in -y (7.5% of the uncertainty, by far the largest effect in the round) and by line position (2.4%). Location adds nothing (0.1%). |
| C19: r/l follows location | location 3.0% (E039) | Not reproduced at the 1% bar: quire 0.5%, line position 0.3%, both tiny. r ≠ l (C16) still stands: it rests on neighbours, not location. |
| C15: e = ee | one sign at word level (E038) | **Restated as word-level only.** At the glyph level, what follows ee differs from what follows e (MIXED, t 0.37), and eee differs from e more than r differs from l. |
| C7: words cluster by topic | I_word 0.387 (E019) | **Restated: words cluster by sheet.** Pages on the same bifolio are more alike than other pages of the same quire (z +6.9 for words, z +6.9 for glyph bigrams); the page next in reading order is not (z +1.3, +0.8). Clustering by sheet (0.397) is stronger than by reading order at the same granularity (0.318). |
| C23: labels echo their page 1.7× | 10.5% vs 6.3% (E051) | **Restated: labels echo their neighbourhood, not their page.** The excess over frequency-matched words is the same on the page's own text (+4.2 points), on the other side of the leaf (+3.4), on the other leaf of the sheet (+3.6) and on the adjacent page of another sheet (+4.5); it is smaller on a random page of the same section (+2.2). Own page vs other leaf: p 0.33. |

## Part A1: the five alternations in one model
"Share" is how much of the uncertainty about which form was written (given the word pair) a factor explains **that no
other factor explains**, after bias correction. PRESENT needs p < 0.001 and share ≥ 1%; TRACE is p < 0.001 but under 1%.

| Alternation | Tokens | Pairs | Line position | Paragraph line | Previous word -y | Scribe | Quire | Section | Headline (pre-registered rule) |
|---|---|---|---|---|---|---|---|---|---|
| **d ±** | 12,504 | 143 | **1.5% PRESENT** | 0.15% trace | **1.9% PRESENT** | 0.0% absent | 0.3% trace | 0.3% trace | **C18 WAS A LINE ARTEFACT** |
| **q ±** | 7,242 | 85 | **2.4% PRESENT** | 0.1% | **7.5% PRESENT** | 0.2% trace | 0.1% | 0.1% | **JUNCTION FORM** |
| r / l | 6,791 | 96 | 0.3% trace | 0.1% trace | 0.0% | 0.1% | 0.5% trace | 0.0% | C19 NOT REPRODUCED |
| t / k | 7,926 | 124 | 0.35% trace | 0.6% trace | 0.0% | 0.4% trace | 0.4% trace | 0.05% | reported |
| e / ee | 5,377 | 73 | 0.2% | 0.1% | 0.0% | 0.0% | 0.3% | 0.0% | reported |

**Plain reading.**
1. **q is mechanical.** Koen G and vosreth's suggestion on the forum is confirmed: a word takes q- mostly when the
   word before it ends in -y. This is a junction (sandhi-like or ligature-like) rule, not a choice of word. **"q as a
   meaning-carrier" is dropped from the attack queue.** Any decoder should treat q- as conditioned on the previous
   word's ending.
2. **d is not a scribe's habit.** E039's result came from not controlling line position and the previous word. The
   d-form is favoured at certain line positions and after -y words. What E039 saw as "scribe 1 uses d less" is the
   A-pages' different line and junction statistics. The A/B difference in *chey/chedy* remains a fact about the
   varieties, but not a scribe habit.
3. **Line position matters most for d and q** (1.5–2.4%), and barely for r/l, t/k and e/ee (0.2–0.4%). The forum's
   "d triples towards line end" is real but modest once the word pair is fixed.
4. **The known-answer controls** show the model does not misattribute: planted line, scribe, quire and junction
   habits each came back on their own factor only (shares 28%, 11%, 19%, 44%; all other factors < 0.2%).

**Caveat.** Scribe, quire and section overlap heavily (hand 1 ≈ Currier A ≈ herbal quires). A factor that explains
nothing "beyond the others" may still be entangled with them; the model says only that scribe adds nothing once
quire, section, line position and the previous word are known. In E039's design the within-quire scribe effect was
2.2%; here it is absorbed by position and junction.

## Part A2: what follows e, ee and eee
Next glyph after a run of e's (prose, 7,706 single e, 3,314 ee, 281 eee). JS = Jensen–Shannon divergence in bits.

| Comparison | JS | Reference |
|---|---|---|
| e vs ee | 0.050 | Latin noise floor 0.001; Latin real-contrast ceiling 0.134; **t = 0.37, MIXED** |
| ee vs eee | 0.055 | |
| e vs eee | **0.165** | larger than r vs l (0.117) |
| t vs k | 0.027 | near-variant, as expected |

What follows: after e, mostly **d** (39%), o (24%), y (21%); after ee, **y** (40%), d (34%); after eee, y (47%), d
(21%), **s** (14%). The forum's observation (s follows eee far more often) is reproduced. **C15 is restated:** e and ee
behave as one sign in which *words* they form (E038), but not in which *glyph* follows them. A cleaned inventory that
merges e-runs loses this information; the merge should be reported as a choice, not a fact.

## Part B1: writing session or reading order?
185 DEV pages with ≥ 50 text tokens; 3,277 pairs with the same scribe and section. Cosine similarity of word counts
(WORD) and glyph bigrams (GLYPH).

| Relation | WORD (same scribe and section) | GLYPH |
|---|---|---|
| L0 same leaf, other side (111 pairs) | 0.377 | 0.904 |
| L1 same sheet, other leaf (158) | 0.388 | 0.902 |
| R1 next page in reading order, other sheet (31) | 0.436 | 0.885 |
| Q same quire, other sheet, not adjacent (470) | 0.424 | 0.881 |
| S other quire (2,507) | 0.284 | 0.824 |

| Test (permutation within quire × scribe × section, 2,000 shuffles) | WORD | GLYPH | Verdict |
|---|---|---|---|
| same sheet vs other sheet in the quire | z +6.9, p 0.0005 | z +6.9, p 0.0005 | **SESSION EFFECT** |
| next page vs other sheet in the quire | z +1.3, p 0.10 | z +0.8, p 0.21 | no adjacency effect |

**Why the raw L1 and Q means look reversed.** The pooled means mix quires: quires with one sheet in DEV contribute
only L1 pairs, and the bathing and stars quires (high similarity) contribute most Q pairs. The permutation null
handles this, which is why the raw difference is negative while z is +6.9. Stratified by quire (post-hoc
description, not a changed rule): same-sheet pages are more similar than other-sheet pages in 7 of 9 quires for words
(mean +0.069) and 9 of 9 for glyph bigrams (+0.042); the next page is not (−0.014 and −0.003).

**Reading.** Pages written on the same piece of vellum resemble each other in vocabulary and in glyph habits; the
page that follows in reading order does not, unless it is on the same sheet. This is quimqu's forum finding,
reproduced on our data with scribe and section held fixed. **C7 is restated:** "words cluster by sheet". That is a
writing-process property, compatible with topic-by-sheet (if sheets were planned by subject), with drift of habits
over sessions, and with a generator that works sheet by sheet. It is no longer evidence of topic as such.

## Part B2: topic clustering by sheet versus reading order
| Chunking | I_word |
|---|---|
| 32 reading-order chunks (C7's definition) | 0.350 (E019: 0.387 on slightly different tokens) |
| 49 reading-order chunks | 0.318 |
| 47 sheets | **0.397** |

Grouping the text by sheet gives *stronger* word clustering than grouping it by reading order at the same
granularity (ratio 1.25). Consistent with B1.

## Part B3: label echo within the sheet, with absolute rates
47 label pages, 964 label words of ≥ 3 glyphs. "Hit" = the label word occurs in the comparison page's text; "base" =
the same for frequency-matched random words.

| Comparison page | hit | base | excess |
|---|---|---|---|
| OWN page | **10.5%** | 6.3% | +4.2 |
| same leaf, other side | 9.2% | 5.8% | +3.4 |
| other leaf of the sheet | 9.4% | 5.8% | +3.6 |
| adjacent page, other sheet | 10.4% | 5.9% | +4.5 |
| random page, same section, other quire | 7.2% | 5.0% | +2.2 |

Own page vs other leaf: Δ +0.6 points, z +0.6, **p 0.33**. Other leaf vs random: Δ +3.1 points, p 0.0005.
**Verdict (pre-registered rule): SESSION ECHO.**

Absolute own-page rates by section: zodiac 9.2% (base 4.0%, 326 labels), cosmological 18.3% (8.9%, 186), bathing
18.4% (12.9%, 87), **pharma 6.5% (5.7%, 200)**, astro 3.6% (4.0%, 139), text pages 14.3% (13.6%, 21). MarcoP's
"about 4 of 200 pharma labels match their paragraph" is at paragraph level; at page level the pharma excess is under
one point, essentially nothing.

**Reading.** A label word is found in the text of its own page no more often than in the text of the neighbouring
pages (same leaf, same sheet, or the next sheet). The echo is a neighbourhood effect of a few quires' vocabulary, not
a tie between a label and the drawing it sits beside. **C23 is restated** as "labels share the local vocabulary of
their part of the book (about +3 to +4 points over frequency-matched words)". Pharma labels, the ones that would name
the drawn plants and jars, show the least.

## Consequences
- **Attack queue:** drop "q as a meaning-carrier"; add "q- is conditioned on the previous word's -y" to the line and
  junction model any decoder must carry (with E025's line rules).
- **Sign inventory:** d± is not to be normalised per scribe; it is a line/junction phenomenon. e-run merging is a
  reported choice.
- **Page-level tests:** every future page-level test (topic, label, picture route) must control for sheet, and the
  simplest control is to compare a page with the other leaf of its own sheet, as done here.
- **For the ledger:** C7 and C23 were never scored, so nothing moves. Both were leaning facts for L; both are now
  writing-process facts that a sheet-wise generator would also produce. The honest range for L (0.60–0.96) is
  unchanged but its lower end is the more defensible reading after this round.
