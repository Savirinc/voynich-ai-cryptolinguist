# E059 pre-registration (clean-up round): line position and writing session as confounds

Written 2026-10-25, before the run. Script: `experiments/e059_cleanup_round.py`. Output:
`experiments/results/e059.json`, `experiments/results/e059_run.log`, report `reports/CLEANUP_ROUND.md`.

## Why
The forum sweep (`FORUM_SYNTHESIS.md`, section 6) raised four threats to measured facts in the ledger. None has been
tested. This round tests them together, as one pre-registered job, so that the facts can be corrected or confirmed
before any further attack relies on them.

| Threat | Fact at risk | Test here |
|---|---|---|
| Glyph mix changes along the line (d triples towards line end, sh halves, qo gives way to o). E038/E039 did not control for line position. | C17, C18 (d is a scribe habit), C19 (q and r/l follow location) | Part A1: one joint model |
| q may be a junction form after a word ending in -y | C19 (q as a possible meaning-carrier) | Part A1: previous-word -y as a factor |
| e / ee / eee have different glyph contexts | C15 (e and ee are one sign) | Part A2: next-glyph distributions |
| The two halves of a bifolio share habits (writing session); the physically next page does not | C7 (topic clustering), C23 (label echo 1.7×); C23 lacks an absolute rate | Parts B1–B3 |

**Terms.** A *bifolio* (sheet) is one piece of vellum folded once, giving two leaves and four pages. In the ZL
transliteration each page carries its quire and bifolio number, so the sheet is known. A *writing session* effect
means pages on the same sheet look alike because they were written together, not because they are about the same
thing. *Line position* is first word, last word, or a middle word of a line.

## Status
A **measurement round under no working assumption**. No ledger factor is pre-registered, because none of the outcomes
separates M, L and C: each outcome corrects or confirms a *fact*, not a hypothesis. (Precedent: E037–E041, E046.)
The ledger gate is met indirectly: C19 feeds the "q as meaning-carrier" line of attack and C23 feeds the picture route,
and both would be dropped or kept by this result.

## Data
- **Text:** Voynich DEV, clean tokens (`is_clean`), LOCKED_TEST leaves excluded (`vcl.corpus.splits.locked_test_leaves`).
- **Part A:** prose tokens with an assigned scribe (hand ≠ '@'): 28,381 tokens. Pairs are E038's minimal pairs with
  both forms ≥ 5 tokens, first-pair rule as in E039 (`e038_sign_inventory_v2.ALTS`, `keep`).
- **Part B:** every DEV page (folio side) with ≥ 50 clean non-label tokens (prose, circle, radial), its word counts and
  its glyph-bigram counts. Labels: clean label tokens of ≥ 3 glyphs on DEV pages with ≥ 20 clean non-label tokens.
- **Latin calibration (A2 only):** latVUC, the first E033 window (28,841 words), exactly as in E038.

## Part A1: the five alternations in one joint model
For every token of a pair word: form f (1 = the form with d, q, k, l or ee; 0 = the other), pair id, and these factors:

| Factor | Levels | Reference level |
|---|---|---|
| POS (line position) | first, mid, last (a one-word line counts as first) | mid |
| PARA (paragraph-first line) | yes / no | no |
| PREVY (previous clean word in the line ends in y) | yes / no (first word of a line: no) | no |
| HAND (scribe) | 1, 2, 3, 4, 5 | 1 |
| QUIRE | the 16 quires | the most frequent quire among the pair tokens |
| SEC (illustration section) | H, P, B, S, Z, A, C, T | H |

Currier A/B is not a separate factor: it is almost the same partition as HAND (hand 1 = A), and E039 used HAND.

**Model.** Logistic regression of f on pair fixed effects plus all six factors, fitted by iteratively reweighted least
squares with a ridge of 1e-4 (numerical stability only). The pair-only model gives deviance D0. For each factor X:
- **LRT:** deviance(model without X) − deviance(full model), with df = levels − 1, p from χ².
- **share:** that deviance difference divided by D0 (how much of the uncertainty about the form, given the pair, this
  factor explains that no other factor explains).
- **share_excess:** share minus its mean under 50 permutations of f within pair cells (bias correction, as E039).
- **stability:** 95% interval of share_excess from 100 page-cluster bootstrap draws (reported, not a criterion).

**Factor verdicts.** PRESENT: p < 0.001 and share_excess ≥ 0.01. TRACE: p < 0.001 and share_excess < 0.01. ABSENT:
otherwise. Tokens in a line are not independent, so the χ² p is anti-conservative; that is why α is 0.001 and a
size bar is added.

**Headline questions.**

| Question | Rule | Reading |
|---|---|---|
| d± (C18) | HAND PRESENT with POS in the model | **C18 STANDS**: d is a scribe habit beyond line position |
| | HAND not PRESENT, POS PRESENT | **C18 WAS A LINE ARTEFACT** |
| | neither PRESENT | C18 NOT REPRODUCED |
| q± (C19) | QUIRE or SEC PRESENT | **C19 STANDS**: location beyond line position and junction |
| | location not PRESENT, PREVY PRESENT | **JUNCTION FORM**: q is mechanical after -y |
| | location not PRESENT, POS PRESENT | LINE ARTEFACT |
| | none PRESENT | C19 NOT REPRODUCED |
| r/l (C19) | same rules as q± | |
| Line position overall | the POS share_excess for each of the five alternations | quantifies the forum's claim |

e/ee and t/k get the same factor table, reported.

**Known-answer controls** (planted on the d± pair tokens, the largest set; each label flipped with probability 0.1):

| Control | Planted rule | Expected |
|---|---|---|
| planted line habit | f = 1 at line end | POS PRESENT, every other factor not PRESENT |
| planted scribe habit | f = 1 for hand 1 | HAND PRESENT, every other factor not PRESENT |
| planted location habit | f = 1 in quires D–H | QUIRE PRESENT, every other factor not PRESENT |
| planted junction habit | f = 1 after a -y word | PREVY PRESENT, every other factor not PRESENT |

If any control misses its planted factor or marks another factor PRESENT, **Part A1 is VOID**.

## Part A2: e, ee, eee by what follows them (C15 at the glyph level)
For every maximal run of e inside a word (prose clean tokens), record its length (1, 2, 3+) and the next glyph (or
end of word). JS is the Jensen–Shannon divergence (bits) between two next-glyph distributions.
- **Voynich:** JS(e, ee), JS(ee, eee), JS(e, eee); reference pairs JS(r, l) (known distinct, C16) and JS(t, k)
  (near-variant) on the same tokens.
- **Latin floor F:** latVUC with each e independently written ee with probability 0.5; JS(e, ee). By construction the
  two distributions are the same, so F measures sampling noise.
- **Latin ceiling C:** mean of JS(e, i) and JS(r, l) in plain latVUC (real letter contrasts).
- **t = (JS_V − F) / (C − F)** for JS(e, ee).

| Verdict | Rule |
|---|---|
| FREE VARIANT (glyph level too) | t < 0.25 |
| MIXED | 0.25 ≤ t < 0.75 |
| DISTINCT | t ≥ 0.75 |
| VOID | C − F < 0.05 bits |

C15 is kept if FREE VARIANT, marked "word-level only" if MIXED or DISTINCT.

## Part B1: writing session or reading order? (page pairs)
For every pair of retained pages **with the same scribe and the same section** (so neither can masquerade as a
session effect), cosine similarity of word counts (WORD) and of glyph-bigram counts (GLYPH). Categories:

| Category | Meaning |
|---|---|
| L0 | same leaf, other side (recto/verso) |
| L1 | same bifolio, other leaf (same sheet, far apart in reading order except for the innermost sheet) |
| R1 | adjacent in reading order, different bifolio |
| Q | same quire, different bifolio, not adjacent |
| S | different quire |

Reading order is the manuscript's page order (folio number, side, sub-number) over all pages, including locked ones
by name only.

**Statistics.** Δ_session = mean(L1) − mean(Q); Δ_adjacent = mean(R1) − mean(Q). Null: 2,000 permutations that
shuffle the physical slot (bifolio, leaf, reading rank) among pages within the same (quire, scribe, section) cell,
recomputing the category means. One-sided p and z for each Δ, for WORD and GLYPH separately. The unrestricted
(all pairs) means are reported for information.

| Verdict (per measure) | Rule |
|---|---|
| SESSION EFFECT | Δ_session p < 0.01 |
| ADJACENCY EFFECT | Δ_adjacent p < 0.01 |
| both / neither | as the two rules fall |

**Reading for C7.** SESSION without ADJACENCY on WORD: C7 must be restated as "words cluster by sheet", a writing
property, not a topic. ADJACENCY on WORD (with or without SESSION): C7 stands as reading-order clustering (which
could still be topic or drift; this test does not decide that). Neither: C7's clustering lives at quire level or
coarser. C8 (persistence of common words) is not at risk from sessions, which would lower it, not raise it; it is not
re-tested.

## Part B2: topic clustering by sheet versus by reading order
I_word as in E019 (types with ≥ 8 tokens; mean entropy deficit of a type's spread over chunks versus 5 shuffles),
on DEV prose clean tokens, under three chunkings: (i) 32 equal reading-order chunks (should reproduce C7's 0.387
within noise), (ii) the 49 sheets, (iii) 49 equal reading-order chunks. Reported: I_sheet / I_reading49. Descriptive,
no verdict: it says whether sheet-level organisation is as strong as reading-order organisation of the same
granularity.

## Part B3: label echo within the sheet (C23), with absolute rates
For every label word w on a label page, and for each comparison page T, hit = w occurs in T's non-label text, and
base = the share of 20 frequency-matched random words (E051's matching: same capped DEV text count) that occur in T.
Excess = hit − base, averaged over labels. Comparison pages:

| Category | Pages T |
|---|---|
| OWN | the label's own page |
| SAME-LEAF | the other side of the same leaf (if ≥ 20 text tokens) |
| OTHER-LEAF | each page of the other leaf of the same bifolio (same session control) |
| ADJACENT | reading-order neighbours not on the same sheet |
| RANDOM | 5 random pages of the same section in a different quire (seeded) |

**Reported:** absolute own-page hit rate (C23 as a rate, overall and by section, including the pharma rate MarcoP
estimated at about 4 in 200), base rates, and excess per category.

**Test.** Per label page, d = excess(OWN) − mean excess(OTHER-LEAF). Null: 2,000 sign flips of d across pages
(the null that a label's own page and its sheet partner are exchangeable). One-sided p.

| Verdict | Rule |
|---|---|
| PAGE-SPECIFIC ECHO | p < 0.01 |
| SESSION ECHO | not page-specific, and excess(OTHER-LEAF) > excess(RANDOM) with sign-flip p < 0.01 |
| NO ECHO | neither |

C23 is kept (restated as a rate) if PAGE-SPECIFIC; replaced by "labels echo their sheet" if SESSION; withdrawn if NO
ECHO. Note for the ledger: page-specific echo is expected under L and C (a label names a thing on the page) **and**
under a self-citation generator that copies label words from nearby text; it is therefore recorded as a fact, not
scored.

## Seed rule (standing rule 8)
Any permutation p that falls in [0.005, 0.02] is re-run with 10 seeds (2,000 permutations each); the verdict is kept
only if ≥ 8 of 10 seeds agree with it, otherwise it is reported as BORDERLINE and the weaker verdict is used.

## What follows
- C15, C17, C18, C19, C23 are confirmed, restated or withdrawn in LEDGER.md by an update-log entry citing E059.
- If q is a JUNCTION FORM, "q as a meaning-carrier" is dropped from the attack queue.
- If SESSION without ADJACENCY, every future page-level test (topic, label, picture route) must control for sheet.

## What was seen before writing this (disclosed)
- E038, E039, E051 and E054 results (in the ledger): d± t_page 0.05, HAND share 12.8%; q± LOCATION HABIT; e/ee FREE
  VARIANT at word level; label echo 10.5% vs 6.3% expected (964 label tokens).
- Forum claims (section 6 of FORUM_SYNTHESIS.md), unmeasured by us.
- Design counts only, computed today: 28,381 prose tokens with a scribe; pair tokens by line position (d± 12,504
  tokens: first 1,020 / mid 10,295 / last 1,189; q± 7,242: 588 / 6,098 / 556; e/ee 5,377; r/l 6,791; t/k 7,926);
  paragraph-first lines hold 19.9% of tokens; 193 DEV pages on 49 sheets (34 sheets have 4 DEV pages); 50 pages with
  labels and ≥ 20 text tokens, all with a sheet partner in DEV.
- **No form-by-position table, no page-pair similarity, no label-echo-by-category number has been computed.**
- The script's functions were exercised on fabricated toy tokens (planted habits) to check they run and recover
  planted effects; no Voynich statistic was produced by that check.
