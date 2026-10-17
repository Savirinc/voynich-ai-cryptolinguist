# E012: Unit inventories — does any choice of Voynich units look like an ordinary alphabet or syllabary, and does solver v2 crack it?

**Scope.** This is structural work plus a calibrated solver test. **No decipherment.** No Voynich word, glyph or unit is
interpreted here. Voynich solver outputs were never stored. Where the solver answered on a Voynich window, we report only
its confidence and the false-answer rates at that confidence.

Code: `src/vcl/corpus/units.py` (inventories and BPE), `experiments/e012_unit_inventories.py`, `tests/test_units.py`.
Results: `experiments/results/e012.json` (all numbers in this report), `e012_stats.json`, `e012_solver_rows.jsonl`
(one row per solver task, with no decodes) and `e012_run.log`.
Command: `caffeinate -ims .venv/bin/python experiments/e012_unit_inventories.py --stage all --workers 3` (seed 12012),
then `--stage resummarise`. The resummarise step only recomputes the solver summary from the saved rows; it makes no new
solver calls.
Compute: the stats stage took 154 s on one process. The solver stage took 1,113 s wall time on 3 workers (about 0.9
CPU-hours of task time). No models were trained and no new dependencies were added.

## 0. Prior work and data

This experiment replicates and extends **Rozanova & Temerev, "A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is
Not a Space: What the Units of Voynichese Are Not", arXiv:2608.17096 (Aug 2026)**. That paper uses the full ZL 3b
transliteration, primary paragraph loci and lines with at least 4 clean tokens. Its controls are 8 prose texts and a
catalogue text.

Our setup differs in four ways:
- **Text.** We use ZL 3b from our hash-checked DOCX (`src/vcl/corpus/ivtff.py`) and only the **DEV leaves**: the 15
  LOCKED_TEST leaves are excluded, and an assertion checks this. We keep prose loci (P), with no minimum of 4 tokens per
  line.
- **Tokens.** A token is clean if it matches `[a-z]+` and contains no `?`. Unclean tokens break adjacency.
- **Size.** This leaves 28,841 clean tokens, 143,950 glyphs, 3,406 lines and 16 quires.
- **Separators.** The parser keeps certain `.` (23,059), uncertain `,` (2,034) and drawing breaks `-` (566) as
  separate classes.

Our controls are **32 corpus languages** (Gutenberg, roles tune+ref only, never test). Each sample has exactly 28,841
words, wrapped into lines with the Voynich DEV tokens-per-line template. Four languages (ceb, gl, ilo, te) have too
little non-test text and are skipped.

## 1. Replication against the paper

| statistic | paper (full ZL) | **ours (DEV)** | agree? |
|---|---|---|---|
| composite-collapsed H(X) / H(X_{t+1}\|X_t) | 3.98 / 2.69 | **3.97 / 2.68** | yes |
| decomposed (raw EVA) H / h_cond | 3.89 / 2.32 | **3.86 / 2.31** | yes |
| within-token-only h_cond (collapsed) | 2.43 | **2.41** | yes |
| h_cond of control languages (letters, spaces removed) | 3.45–3.52 (4 texts) | 32 languages: median 3.61, range 2.95 (tl) – 4.03 (he); **31/32 ≥ 3.41** | yes. Tagalog (2.95) is the only language within 0.3 bits of Voynich. |
| adjacent-token MI, 2,000-type cap, within-line shuffle (100) | 0.066 bits, **0.79%** of H(T) | **0.064 bits, 0.75%** | yes |
| … with uncertain spaces merged | 0.54% | **0.46%** | yes |
| … control languages | 2.0–9.7% | 32 languages: **3.2% (pl) – 12.3% (el)** | yes: Voynich is far below every language |
| edge-glyph MI (last → first glyph, collapsed), shuffle-corrected | **0.197 bits, 5.7%** | **0.191 bits, 5.7%** (raw EVA 0.181) | yes |
| share of observed edge MI destroyed by shuffling | 88–93% | 89% | yes |
| largest edge pair | y→q ≈ half | y→q 0.094 of 0.213 observed bits; then r→a, s→a | yes |
| edge MI of control languages (letters) | 0.018–0.120 | 32 languages: median 0.051, **max 0.166 (fr)** | yes: Voynich is above all 32 |
| share of word types seen once (hapax) | 69.7% (at 32,747 tokens) | **67.8%** (at 28,841) | close. **But our 32 languages range from 56% to 73%** (fi 73%, pl 71%), so the hapax share alone does **not** set Voynich apart. The paper's "just above the control maximum" (67.7%) depends on its 8 controls. |
| hapax share, uncertain spaces merged | 73.0% | 71.4% | yes |
| adjacent tokens within one edit, observed/shuffled | 1.12 | **1.15** (languages 0.19–1.13) | yes |
| internality index I, uncertain `,` | 0.494 | **0.476** | yes |
| I, certain `.` | 0.029 | **−0.086** | same ordering; slightly lower level |
| I, first separator / mid-line / line break | 0.099 / 0.064 / −0.036 | 0.002 / −0.047 / −0.185 | same ordering; levels lower |
| BPE dependence D_k (raw, within-token), k = 0/16/32/64/128/256 | 1.595 / – / – / **1.045** / 1.119 / 1.475 | 1.553 / 1.207 / 1.130 / **1.025** / 1.154 / 1.504; minimum at 64 (89 types) | yes |
| D_k after collapsing the composites first | trough at 32–64 (1.049 / 1.046) | 1.052 / 1.046 at 32 / 64 | yes |
| Currier A / B minimum | 64 / 64 | A: 32 (1.063; 64 = 1.085). B: 64 (1.147) | approximately |
| cross-fit (learn on 15 quires, score the held-out one) | 1.686 / 1.423 / 1.379 / 1.490 at k = 0/16/32/64; minimum at 32 | 1.645 / **1.385** / 1.411 / 1.488; minimum at **16** (32 is within 0.03 bits) | values agree; the argmin moves one checkpoint |
| random half-quire splits: overlap of compound units at k = 64 | 83.9% | **80.5%** (median of 20 splits); argmin 64 in 30 of 40 half-fits, 32 in 10 | yes |
| space-erased BPE at k = 64: share of certain / uncertain / all positions crossed | 2.5% / 20.3% / 60.0% | **2.2% / 18.5% / 60.1%** | yes |
| Latin word boundaries crossed after space erasure | 15.5% | 12.6% (our Latin sample) | yes |

**Summary.** Every headline number replicates on our DEV-only data to within about 0.05 bits or a few percentage points.
Two numbers disagree:
- The certain-separator and line-break internality levels are lower than the paper's. The ordering is the same.
- The hapax share does not separate Voynich from a broader set of 32 languages.

## 2. Inventories compared

| inventory | definition | types | h1 | h_cond | h_cond/h1 | units per word (mean, CV) | edge MI bits |
|---|---|---|---|---|---|---|---|
| raw EVA | one character per unit | 25 | 3.86 | 2.31 | 0.60 | 4.99, 0.36 | 0.182 |
| composite-collapsed | paper's 9 composites | 34 | 3.97 | 2.68 | 0.68 | 4.07, 0.36 | 0.191 |
| Zattera slot alphabet | 26 slot characters (see note) | 35 | 4.04 | 2.59 | 0.64 | 4.21, 0.35 | 0.190 |
| BPE V = 40 | within-token BPE learned on DEV | 40 | 4.77 | 3.55 | 0.74 | 3.03, 0.42 | 0.217 |
| BPE V = 80 | " | 80 | 5.79 | 4.76 | 0.82 | 2.17, 0.45 | 0.265 |
| BPE V = 150 | " | 150 | 6.61 | 5.47 | 0.83 | 1.81, 0.48 | 0.277 |
| BPE V = 300 | " | 300 | 7.46 | 5.89 | 0.79 | 1.55, 0.48 | 0.233 |
| space-erased BPE V = 80 | BPE on line strings with spaces deleted | 80 | 5.77 | 4.74 | 0.82 | (no words; mean unit span 2.33 glyphs) | – |
| *32 languages, letters* | | *26–77 (median 36)* | *4.20* | *3.61 (2.95–4.03)* | *0.85 (0.81–0.93)* | *4.61, 0.56 (CV 0.38–0.65)* | *0.051 (max 0.166)* |
| *32 languages, syllables* | | *1,148–8,211* | *8.77* | *4.64* | *0.52* | *1.75, 0.53* | *0.39 (max 0.84)* |

The language rows give medians, with ranges in parentheses. BPE rows for the languages use the same procedure at the
same vocabulary size (letters as the base). They are in `e012.json["languages"]["profiles"]`.

**Slot alphabet source.** M. Zattera, "A New Transliteration Alphabet Brings New Evidence of Word Structure and
Multiple 'Languages' in the Voynich Manuscript", ICVM 2022, CEUR-WS Vol-3313 paper 10, Figure 3. **Verified** on
2026-10-17 by reading the CEUR PDF. The 26 characters are q s d o y l r t k p f ch sh cth ckh cph cfh e ee eee a i ii
iii m n. The Currier / v101 alphabets were not used.

**Placement in the language cloud.** Each inventory is placed against the language cloud built with the matched
procedure.
- **Features:** log types, h1, h_cond, h_cond/h1, mean and CV of units per word, unit Zipf slope and edge share.
- **Distance:** RMS z against the 32 languages.
- **"Inside":** the distance is at or below the 95th percentile of the languages' own leave-one-out distances.

| Voynich inventory | vs letters | vs syllables | vs same procedure on languages | features with abs(z) ≥ 2 (matched procedure) |
|---|---|---|---|---|
| raw | 5.04 (p95 2.19) **out** | 12.1 out | = letters | h_cond, h_cond/h1, wl_cv, edge |
| collapsed | 3.75 **out** | 10.8 out | = letters | h_cond, h_cond/h1, wl_cv, edge |
| slot | 4.20 **out** | 10.7 out | = letters | h_cond, h_cond/h1, wl_cv, edge |
| BPE 40 | 2.56 out | 6.93 out | 2.24 (p95 2.08) **out** | h_cond/h1, wl_cv, edge |
| BPE 80 | 4.27 out | 4.58 out | **1.31 (p95 2.04) INSIDE** | wl_cv |
| BPE 150 | 6.33 out | 3.40 out | **1.50 (p95 2.22) INSIDE** | wl_mean, wl_cv |
| BPE 300 | 8.25 out | 2.91 out | **1.90 (p95 2.10) INSIDE** | h_cond, h_cond/h1, wl_mean, wl_cv |
| space-erased BPE 80 | – | – | 2.87 (p95 1.72) out | span (units are longer than in any language) |

The twins, re-tokenised with exactly the same procedure, have these RMS z distances against the BPE-80 / BPE-150 cloud:

| twin | BPE-80 | BPE-150 |
|---|---|---|
| naibbe_exact la / it / fr | 2.70 / 2.71 / 2.70 | 1.99 / 2.19 / 2.19 |
| self_citation | **1.79** | **2.04** |
| abbreviation/enm | 1.89 | 2.24 |
| syllabary/cs | 4.09 | 5.23 |
| Naibbe-style (approximation)/it | 10.2 | 6.5 |
| rugg_grille | 13.9 | 13.2 |

So **the meaningless self-citation generator is also inside the BPE-80 and BPE-150 clouds**.

Word-level placement against the 32 languages uses hapax share, token-MI share, top-50 coverage and the edit-1 ratio.
Voynich is at 2.35 against a p95 of 2.06, so it is **out**: token MI has z −3.2 and the edit-1 ratio has z +3.1. The
naibbe_exact twins (2.0–2.3) and abbreviation (0.9) are closer than Voynich.

**Reading the placement.**
1. Under every fixed inventory (raw, collapsed, slot), Voynich is **far outside** the letter cloud and the syllable
   cloud. Re-segmenting into the paper's composites or Zattera's slot characters raises h_cond from 2.31 to 2.59–2.68.
   It does not reach any language (min 2.95, median 3.61). Word-length dispersion (CV 0.35 against at least 0.38) and
   edge coupling also stay outside.
2. Learned units at V = 80–300 put Voynich **inside** the cloud of languages tokenised the same way. This is **not
   evidence of language**:
   - Matched-vocabulary BPE forces types and h1 to agree by construction, and it compresses the other features.
   - The meaningless self-citation generator and the verbose naibbe_exact cipher land at the same distances, so at
     this scale the cloud membership cannot tell language, cipher and gibberish apart.
   - Word-length dispersion stays outside at every scale: Voynich has fewer, more uniform units per token.
3. **Verdict on question 3: no inventory makes Voynich look like an ordinary alphabet or syllabary.** The only
   "inside" results occur where the test has no discriminating power. Section 5 shows that edge coupling is the
   feature that resists every unit choice.

## 3. Solver v2 with calibration

**Setup.**
- **Solver:** v1 plus self-null abstention, with the E005 margin of 0.00506 and the v1 calibrator threshold of 0.62.
- **Windows:** 250 Voynich DEV tokens; 6 windows spread evenly through the manuscript for each inventory.
- **Long windows:** BPE 80, 150 and 300 were also run on 750-token windows (3 Voynich windows each).

Calibration streams (each condition below was run for every inventory):

| condition | how it is built | what counts as a false answer |
|---|---|---|
| ka_letters | Known-answer substitution of real tune-book text (la, it, de, fr, es, cs), **matched in symbol count and unit-type count** to that inventory's Voynich windows. Mono if the type count is at most the letter count; otherwise homophonic with homophones allocated by frequency. Spaces are removed for the erased inventory. | a decode below 0.9 char accuracy |
| ka_syllables | One symbol per syllable, same symbol count | any answer |
| naibbe_exact | Greshko's published tables (la, it, fr), re-tokenised with the inventory | any answer (no letter-level reading is possible; every answer was wrong) |
| decoys | Rugg-grille and self-citation twins (E011 specs, BPE learned on the twin itself), and order-3 Markov surrogates of the Voynich unit stream | any answer |

Gate 1 (PROTOCOL §4): at least 90% of the matched known-answer letter ciphers must be solved (char accuracy ≥ 0.9).
Otherwise the Voynich run at that scale is **VOID**.

| inventory (window) | known-answer letters solved | Gate 1 | syllable ciphers answered | naibbe_exact answered | decoys answered | Voynich windows answered |
|---|---|---|---|---|---|---|
| raw (250) | **6/6** (mono, acc 0.99) | **pass** | 0/3 | 0/3 | 0/6 | **0/6** (max conf 0.35) |
| collapsed (250) | 5/6 (one 25-symbol homophonic failed) | fail → VOID | 0/3 | **1/3 answered, char acc 0.00, conf 0.68** | 0/6 | 1/6 (conf 0.65), VOID |
| slot (250) | 5/6 | fail → VOID | 0/3 | 0/3 | 0/6 | 0/6 (max 0.54) |
| BPE 40 (250) | 3/6 | fail → VOID | 0/3 | 0/3 | 0/6 | 1/6 (conf 0.72), VOID |
| BPE 80 (250) | 3/6 | fail → VOID | 0/3 | 0/3 | 0/6 | 0/6 (max 0.05) |
| BPE 80 (750) | **4/4** (homophonic K≈71, acc 0.99) | **pass** | 0/1 | 0/1 | 0/3 | **0/3** (max 0.22) |
| BPE 150 (250 / 750) | 0/6 / 1/4 | fail → VOID | 0 | 0 | 0 | 0/6 / 0/3 |
| BPE 300 (250 / 750) | 0/6 / 0/4 | fail → VOID | 0 | 0 | 0 | 0/6 / 0/3 |
| space-erased BPE 80 (250) | 0/6 | fail → VOID | 0/3 | 0/3 | 0/6 | 0/6 |

Pooled results:
- **Decoys:** 0 of 57 answered, so the decoy false-positive rate is 0.00 (95% upper bound about 0.05).
- **All non-letter calibration streams:** 1 of 111 answered (0.009). The one answer was on a *meaningful* naibbe_exact
  cipher, and it was wrong.

**The two Voynich windows that were answered.** Both are in VOID inventories, and **neither is a reading**:
1. **BPE 40, window at token 17,154: confidence 0.72.**
   - Decoys in the same inventory with confidence ≥ 0.72: 0/6.
   - Non-letter streams with confidence ≥ 0.72: 0/12 in this inventory, 0/111 pooled.
   - Gate 1 failed at this scale (3/6), so the run is **VOID**.
2. **Collapsed, window at token 22,872: confidence 0.65.**
   - Decoys with confidence ≥ 0.65: 0/6.
   - **The naibbe_exact/fr cipher was answered at confidence 0.68 with character accuracy 0.00.** It was decoded as
     the wrong language and passed the self-null test. So at this confidence a known-false answer exists within this
     inventory: the non-letter false-answer rate is 1/12, or 1/111 pooled.
   - Gate 1 failed (5/6), so the run is **VOID**.
   - Post-hoc diagnostic, not preregistered: both Voynich decodes have language-model gaps of 0.80 and 0.94. Every
     correct known-answer decode had a gap of 0.03–0.49, and the wrong naibbe answer had 1.01. Both Voynich answers
     sit in the false-answer range.

In the only two settings that pass Gate 1 (raw EVA and BPE-80 on 750-token windows), solver v2 **answered no Voynich
window** (0/6 and 0/3). By protocol this is a valid "no letter-substitution solution found" result. It holds only for
mono/homophonic letter substitution over these units, with the 36-language library.

**Solver limits shown by calibration.**
- At the 250-token scale the solver cannot reliably solve a homophonic cipher with 40 or more types (BPE 40–300).
- It never solves space-erased streams.
- By design it cannot read syllable-unit or verbose (Naibbe) ciphers. It abstained on 26 of 27 Naibbe streams and all
  27 syllable streams; the one answer was wrong.

So "no answer" on Voynich at these scales is uninformative, except for raw EVA and BPE-80 at 750 tokens.

## 4. Edge coupling: the target for future twin generators

The edge feature is the shuffle-corrected MI between the last unit of token t and the first unit of token t+1. The
tokens are taken at the same unit scale for every corpus.

| scale | Voynich bits (share of H(first)) | 32 languages: median / max bits | naibbe_exact la / it / fr | self-citation | Rugg grille (approx.) | Naibbe-style approx. / syllabary / abbreviation |
|---|---|---|---|---|---|---|
| raw EVA (languages: letters) | **0.182 (5.9%)** | 0.051 / 0.166 | 0.003 / 0.002 / 0.002 | −0.001 | 0.240 | 0.033 / 0.007 / 0.024 |
| collapsed | **0.191 (5.7%)** | 0.051 / 0.166 | 0.005 / 0.004 / 0.003 | −0.001 | 0.300 | 0.047 / 0.009 / 0.027 |
| slot | **0.190 (5.7%)** | 0.051 / 0.166 | 0.003 / 0.004 / 0.003 | −0.001 | 0.268 | 0.037 / 0.010 / 0.027 |
| BPE 40 | 0.217 (5.1%) | 0.072 / 0.246 | 0.019 / 0.022 / 0.016 | −0.001 | 0.888 | 0.214 / 0.030 / 0.055 |
| BPE 80 | 0.265 (5.0%) | 0.215 / 0.507 | 0.069 / 0.071 / 0.070 | 0.001 | 1.98 | 0.52 / 0.135 / 0.133 |
| BPE 150 | 0.277 (4.3%) | 0.331 / 0.706 | 0.139 / 0.141 / 0.145 | 0.004 | 3.05 | 0.76 / 0.44 / 0.25 |
| BPE 300 | 0.233 (3.2%) | 0.430 / 0.864 | 0.172 / 0.184 / 0.198 | 0.008 | 3.55 | 0.79 / 0.62 / 0.37 |

**Takeaways.**
- **At glyph scale (raw, collapsed, slot), Voynich's edge coupling, about 0.19 bits, is above all 32 languages**
  (max 0.166, French). It is 40–80× that of the faithful Naibbe cipher (0.002–0.005 bits; the paper reports
  0.006–0.009). Self-citation has none.
- With learned units, language edge MI grows quickly: whole morphemes start to sit at word edges. Voynich's stays flat
  at about 0.2–0.28 bits, so at V ≥ 80 Voynich drops below the language median.
- Voynich's coupling is concentrated in a few glyph pairs: y→q alone carries about 0.09 of the 0.21 observed bits.
  That is a glyph-level junction rule, not word-to-word content.
- Our Rugg-grille approximation over-produces edge MI (0.24–0.30 bits at glyph scale). It does this because its table
  cells chain fixed suffix/prefix chunks. It also has a closed 212-type vocabulary (hapax 0%), so it fails elsewhere.
- **Target for twin generators:** about 0.19 bits (5.7% of H(first glyph)) at glyph scale, 89% destroyed by
  within-line shuffling, about half of it from y→q, together with token-identity MI ≤ 0.8% and hapax about 68%. No
  current twin produces all of these at once.

## 5. Verdict

1. **Replication.** The paper's unit-level findings replicate on DEV-only data: h_cond 2.68 (collapsed), token-order
   share 0.75%, edge MI 0.19 bits, uncertain-separator internality 0.48, a BPE trough at 64 merges with about 80% half-
   split overlap, and 2% / 18% / 60% crossing after space erasure. The one disagreement is the hapax share. Across 32
   languages (56–73%), Voynich's 68% is ordinary, so it is not a discriminator at this sample size.
2. **Inventories.** No principled inventory puts Voynich inside the natural-language cloud on a test that can
   discriminate:
   - Fixed alphabets (raw, collapsed, Zattera slot) stay far outside both the letter cloud and the syllable cloud.
   - Learned BPE units at V = 80–300 fall inside the matched-procedure cloud, but so do a meaningless generator and a
     verbose cipher.
3. **Solver.**
   - Gate 1 passed for raw EVA and for BPE-80 on 750-token windows. On those, solver v2 answered no Voynich window.
   - All other scales are VOID: the solver cannot crack matched known-answer ciphers there.
   - The two answered Voynich windows were both in VOID scales, and at one of their confidence levels a known-false
     answer (Naibbe) exists. They are **not readings**. **No decipherment.**
4. **Edge coupling.** This is the robust discriminator. At glyph scale it is above every language, 40–80× the
   faithful Naibbe cipher, and at least 4× every other language-carrying twin we tested. No re-segmentation removes it.

## 6. Caveats and unverified items

- **Our data differ from the paper's.** We use DEV leaves only (about 85% of prose), keep all prose lines (the paper
  requires at least 4 clean tokens), and treat unclean tokens as adjacency breaks. Our controls are Gutenberg samples
  of 32 languages, not the paper's genre-matched texts. Edge, token-MI and edit-1 statistics on the language clouds use
  20 shuffles; Voynich uses 100.
- **BPE is our own implementation.** It is deterministic: ties go by count, then lexicographic pair. Vocabulary size
  is base alphabet plus merges, so for languages with more than 40 letters, BPE-40 has 0 merges.
- **Known-answer matching is approximate.** The letter ciphers are matched on symbol count and unit-type count, but
  mono vs homophonic depends on the language's alphabet. Calibration samples are small: 4–6 known-answer ciphers, 3
  Naibbe streams and 6 decoys per inventory. Gate 1 at 5/6 (0.83) is coarse. The decoy false-positive rate of 0/57 has
  a 95% upper bound of about 0.05.
- **The gap diagnostic in §3 is post hoc.** It is not part of solver v2 and is not used to accept or reject anything.
- **Twin approximations are reused unchanged from E011.** These are the Naibbe-style, Rugg and self-citation
  approximations. naibbe_exact uses the published tables. A twin's failure is not a refutation of the original
  proposal.
- **Syllabification is crude.** It uses the onset-maximal orthographic rule from `twins.syllabify`. For Hebrew and
  other scripts without written vowels it yields whole words.
- **Verification status of sources.**
  - Zattera 2022 slot alphabet: verified by reading the PDF.
  - Rozanova & Temerev: read in full (local PDF copy).
  - We did not obtain the paper's code (`github.com/lrozanova/voynich-units`) or check it, so some estimator details
    are our reading of the text.
- **LOCKED_TEST leaves were not read.** No Voynich decode was stored or inspected.
