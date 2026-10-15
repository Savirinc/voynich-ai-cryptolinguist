# WS-E — Independent adversarial review (Agent 8)

Scope: `workstreams/ws_a_cryptanalysis`, `ws_b_abbreviation`, `ws_c_generative`, `ws_d_zodiac` (RESULTS.md, results.json, code, logs), `REPORT.md`, `ledger/HYPOTHESIS_LEDGER.md`, `BLIND_EVALUATION/PREREGISTRATION.md` and `run_blind.py` (source only). `blind_results.json` and `run_blind.log` were NOT opened. No blind-leaf token was loaded by any WS-E script (`e_common.py` filters `HOLDOUT.json blind.all_blind_leaves` at load and asserts).

Compute used by WS-E: ≈ 11 CPU-min (`rep_a_mi.py` 6 s; `rep_c_abjad.py` ≈ 60 s; `rep_d_register.py` ≈ 60 s; `rep_b_wsc.py` 419 s; `break_a2_learned_punk.py` ≈ 100 s). All scripts and logs are in this directory (`logs/*.log`, `logs/*.json`).

---

## 1. Leakage audit

### 1.1 Blind-leaf exclusion — every corpus load path

| Path | File:line | Filter | Verdict |
|---|---|---|---|
| WS-A | `ws_a_cryptanalysis/common.py:20` (`load_voynich`) | `int(r['leaf']) not in BLIND` in the CSV comprehension; `assert` at :31 | OK. All m1–m4b scripts load only through `C.load_voynich`. |
| WS-B | `ws_b_abbreviation/common.py:15-17` | filter immediately after `DictReader`, then `assert` | OK. m1b/m1c/m4b/m4c `exec()` slices of other scripts but the only data loader is `load_voynich`. |
| WS-C | `ws_c_generative/common.py:27-28` | `df[~df.leaf.isin(blind)]` before any use; labels (`:35`) taken from the already-filtered `df` | OK. `models_cipher.py` reads only Latin corpora. |
| WS-D | `ws_d_zodiac/scripts/zodiac_tests.py:19-22` | filter + `assert` | OK. |
| WS-D | `ws_d_zodiac/scripts/build_figure_table.py:36-41` | parses **raw IVTFF** (not the CSV) but whitelists six folio ids; `assert 72 in blind` at :24 | OK by whitelist, not by the shared filter. I verified `figure_table.csv` contains only f70v2/f70v1/f71r/f71v/f73r/f73v (155 L-loci on these pages in the CSV; 135 Lz-loci in the table). |
| shared `code/textstats.py`, `code/cipher_search.py`, `code/generators.py` | — | no data loading | OK. |
| round-1 `code/phase2_*.py`, `phase3_*.py`, `phase4_semantic.py`, `audit_gloss.py` | e.g. `code/phase3_fingerprint.py:4` | load `eva_takahashi.txt` **with no blind filter** | Not a violation of the round-2 rule (these ran before `HOLDOUT.json` existed), but see §1.3. |

Partition integrity (my check, `rep_a_mi.py` preamble / inline python): blind ∩ dev-folds = ∅; folds are pairwise disjoint; every non-blind leaf (102 − 11 = 91) is in exactly one fold; folds are keyed by physical `leaf` (both sides together). Multi-panel folios f70v1/f70v2 → leaf 70, f72r1–f72v3 → leaf 72: the `f408f7f` re-freeze fixed this correctly.

### 1.2 Minor exposure (reported, not a violation of the token rule)
- `ws_d_zodiac/logs/https___www.voynich.nu_writing.html` and `logs/index.html.html` are raw web snapshots that contain the voynich.nu month-name table rows for the blind leaf 72 (`f72r1 Taurus may`, `f72r2 Gemini jong`, `f72r3 Cancer iollet`, `f72v3 Leo augst`, …) and quire-layout notes mentioning f72. These are Latin-script marginal annotations and page metadata, not Voynichese tokens, and `IMAGE_ANCHORS.md` explicitly omits the leaf-72 rows from its catalog. Severity: low; recommend deleting the two HTML snapshots or redacting the f72 rows before unblinding is declared complete.
- WS-D self-reported that a first IIIF crop (x 0–2900) showed a sliver of blind f72r and was deleted at once (`logs/image_acq.log`). Accepted as handled.

### 1.3 "Computed on full corpus, reported as held-out" check
- WS-A/B/C/D: every Voynich statistic in the four RESULTS files is computed on the non-blind set, and the fold statistics are fit-on-4/eval-on-1 at leaf level. I found **no instance** of a full-corpus number presented as held-out. One wording issue: WS-A M1 and WS-A M4b entropy tables, WS-B M2 Voynich A/B h2, and WS-C "Real values (all non-blind dev prose, 29,983 tokens)" are *whole-dev-set* descriptive statistics, not cross-validated; they are labelled as such, so acceptable.
- WS-A M2: fold-0 JSON was overwritten by the folds-1,2 run; the fold-0 numbers in RESULTS come from `logs/m2_smoke.log:6`. I checked the log line (score −3.292, params 89, test LL −3.177, att5 16.1 %, n=2210) matches RESULTS. OK.
- **Structural finding (not a code violation):** `HOLDOUT.json` was frozen at 03:03, *after* the round-1 report (02:42) and ledger were written from the full Takahashi corpus (`code/phase3_*.py` load everything). Every round-1 number in `REPORT.md` §3 and ledger rows H2–H10 — including the y→q dependence, line-final -m, h2 = 2.0–2.1, the 86 % slot-grammar coverage — was computed *with the now-blind leaves included*. The blind set is therefore blind to round-2 **code**, not to the **hypotheses**. Pre-registered predictions P3–P6 (y→q ≥ 0.20 gap; line-final m ≥ 0.40/≤ 0.15) are properties already measured on those leaves in round 1 (and long known in the literature). Their "pass" on the blind set would be confirmation of generalisation across leaves, not an out-of-sample prediction. This must be stated when the blind results are reported.

### 1.4 Dev-fold usage
- WS-A M2 ran 3 of 5 folds (budget); WS-A M3 3 of 5; WS-B M1 decoder folds 0,1 only. Reported as such — fine, but "mean ± sd" over 3 folds should not be compared 1:1 with 5-fold figures.
- WS-A M1 (MI, BPE) is **not** cross-validated at all (no fitting involved, so acceptable); the BPE segmenter is fit and scored on the same 2,500 lines (unsupervised; F1 is in-sample). Minor.

**Violations found: none** against the blind-token rule. One low-severity metadata exposure (§1.2); one program-level design issue (§1.3).

---

## 2. Claim-by-claim replication

All WS-E replications use independent code (`e_common.py`) except (b), which deliberately re-runs WS-C's own harness on two folds as instructed.

| # | Claim (source) | Original value | WS-E value | Replicates? |
|---|---|---|---|---|
| a1 | Cross/within MI ratio, Voynich all, EVA chars (WS-A M1) | 0.097 | 0.097 (cross 0.163 / within 1.672) | **Y** (exact) |
| a2 | … Voynich all, EVA units | 0.140 | 0.140 | **Y** |
| a3 | … Voynich A units / B units | 0.120 / 0.159 | 0.120 / 0.159 | **Y** |
| a4 | Latin true spaces ratio (Voynich layout) | 0.064 | 0.065 (different relayout seed) | **Y** |
| a5 | Latin random spaces ratio | 0.979 | 0.999 | **Y** (both ≈ 1) |
| a6 | Latin every-5 ratio | 1.01 | 0.989 | **Y** |
| a7 | Voynich units word-shuffle null | 0.024 ± 0.001 | 0.0247 ± 0.0010 (20 reps) | **Y** |
| a8 | *WS-E addition:* Latin with spaces at syllable-like (…vowel-group) boundaries | — | ratio **0.322**, h2 2.76 | Shows a non-random, non-word boundary rule sits *between* the two bands; "spaces are genuine unit boundaries" holds, "spaces are word boundaries" is not established by this test alone. |
| b1 | M2 char5 unconditioned, folds 0/1 (WS-C) | 11.758 / 12.436 | 11.758 / 12.436 | **Y** |
| b2 | M2 char5 full-cond λ=.8, folds 0/1 | 11.498 / 12.198 | 11.498 / 12.198 | **Y** |
| b3 | M5 cipher-of-Latin V=1000, folds 0/1 | 12.597 / 13.184 | 12.597 / 13.184 | **Y** (deterministic) |
| b4 | Conditioning gain M2 plain → full | 0.24–0.30 | 0.26 / 0.24 (λ=.8); 0.29 / 0.29 (λ=.6) | **Y** |
| b5 | "M5 loses to M2 char5 by ≈0.8 bits" | 0.81 ± 0.07 | +0.839 / +0.749 | **Y numerically — but see §3: the number is the fixed mixture prior, not a likelihood comparison** |
| c1 | Voynich A / B h2 (fold mean ± sd) (WS-B) | 2.12 ± 0.05 / 1.99 ± 0.06 | 2.123 ± 0.060 / 1.984 ± 0.068 | **Y** |
| c2 | Vowel-deleted Latin h2 ≥ 2.9 | 2.90–3.22 (all langs) | latin_medieval 3.163, latin_technical 3.149, latin_all 3.184, Occitan 3.069, ME 3.050, German 3.222, Old French 2.930, **Italian 2.885** | **Y** within 0.02; the floor is 2.89 (Italian), not 2.90 — immaterial |
| c3 | Vowel → single marker h2 2.40–2.80 | 2.40–2.80 | 2.40 (Italian) – 2.81 (German) | **Y** |
| c4 | Vowel deletion leaves wl-sd 1.3–1.8 (Ger 2.8) | 1.28–1.79 | 1.28–1.78 (Ger 2.84) | **Y** |
| d1 | First-glyph JS, zodiac labels vs same-page circular text (WS-D) | 0.139 bits, null 0.014, p = 0.0005 | **0.139**, WS-D-style null 0.012, p = 0.0005; **proper group-permutation null** 0.026 ± 0.009, p = 0.0005 (2000 reps) | **Y** |
| d2 | ot/ok/op/of-initial share 0.705 vs 0.373 | p = 0.0005 | 0.705 vs permutation null 0.445, p = 0.0005; using *all* 155 clean L-loci on those pages (CSV, not WS-D's parser): 0.619 vs 0.374/0.445, p = 0.0005 | **Y** |
| d3 | *WS-E addition:* leaf-level robustness | — | ot/ok-initial labels vs circular: leaf 70 0.69/0.35, leaf 71 0.66/0.46, leaf 73 0.53/0.30 | Effect present on each of the 3 usable leaves (not driven by one page) |

Not independently replicated (budget; verdicts accepted on documentation): WS-A BPE boundary F1, WS-A M2/M3/M4 search results, WS-B decoder/ILS results, WS-B M3/M4, WS-D H-deg/H-copy/H-decan permutation tests. These are all *negative* results whose logic I audited in code; none bears a positive claim.

---

## 3. Break attempts on the strongest structural claim

**Target claim (WS-C):** "content-free conditioned models beat cipher-of-language models by ≥ 1 bit/word on every fold and reproduce the y→q and line-final -m effects."

### 3.1 Weakest-link analysis
M5 is defined (`models_cipher.py:115, 162-176`) as a mixture: with probability `p_unk` the word is emitted by a **char-5 LM of Voynich words identical to M2**, otherwise by lexicon→channel. `p_unk = 0.449` is **fixed from the Latin corpus coverage** (`Lexicon.__init__`, :35), never learned from Voynich. Hence, if the lexicon+channel component carries *no* information about Voynich words, M5 must lose to M2 by about −log₂(1 − 0.449) = **0.86 bits/word**, regardless of anything else. The observed loss is 0.81 ± 0.07. The headline margin is therefore predicted by arithmetic, not by the data. (The pruning-to-K argument in RESULTS, "bits are an upper bound biased against the cipher", is correct but describes a far smaller bias; the dominant bias was not acknowledged.)

### 3.2 Tests run (`rep_b_wsc.py`, `break_a2_learned_punk.py`; logs `logs/rep_b_wsc.log`, `logs/break_a2.log`)

| Test | Result |
|---|---|
| **A. Sweep p_unk after fitting (fold 0, unigram-LM scoring)** | p_unk 0.449 → 12.62; 0.6 → 12.29; 0.8 → 11.97; 0.9 → 11.84; 0.97 → 11.77; **0.995 → 11.755** (M2 plain = 11.758). The curve is monotone to the UNK-only limit: the lexicon component is worth ≤ 0.003 bits. |
| **A2. Learn p_unk on TRAIN only (400 training lines, grid), score dev** | Fold 0: selected p_unk = 0.995, dev 11.755 (fixed-prior 12.619; M2 11.758). Fold 1: selected 0.995, dev 12.430 (fixed 13.201; M2 12.436). With one extra learned parameter the "cipher model" reduces to M2 and the 0.8-bit gap vanishes. |
| **B. Larger EM budget (fold 0): em_sub 600 → 2400, iters 4 → 8, K 30 → 60** | M5 Latin 12.597 → **12.401**. Improvement 0.20 bits, still 0.64 above M2 plain, 0.90 above M2 cond. Train LL still improving at iter 8 (−8.40 nats, Δ ≈ 0.025/iter) — not converged, but the slope is shallow. Does **not** overturn. |
| **C. Scrambled-Latin lexicon under the same larger budget** | 12.436; Latin − scrambled = **−0.035** (Latin slightly *worse*). The decisive null replicates and strengthens under more EM: the channel learns a length/frequency profile, not Latin. |
| Positive control re-read in this light (`logs/run_cipher_control.log`, 04:01 run) | On a true verbose cipher M5 (fixed p_unk 0.449) *beats* M2 by 0.07 bits ⇒ the lexicon+channel component there contributes ≈ 0.86 + 0.07 ≈ **0.93 bits/word**. On Voynich it contributes ≈ 0.00. That is the real, and larger, separation. |

### 3.3 Outcome
The claim as *phrased* ("content-free models beat cipher models by ≥ 1 bit/word") does not survive: the ≥ 0.8-bit component of the margin is the fixed mixture prior and disappears when the prior is learned. The claim as *meant* survives and is stronger when restated correctly:

> The Latin (or Italian / Old French) lexicon→verbose-channel component, when allowed to compete with a Voynich char-5 model for probability mass, is assigned ≈ 0.5 % of the mass by the training data and contributes ≤ 0.003 bits/word on held-out leaves, versus ≈ 0.9 bits/word on a synthetic verbose cipher of Latin; its gain over a scrambled lexicon is −0.02 to −0.04 bits even with 4× EM data and 2× iterations. Independently, conditioning a char model on {previous word's last glyph, line-last flag} gains 0.24–0.30 bits/word (replicated).

Consequence for the pre-registration: **P1** (`bits(M2cond) < bits(M5lat) − 0.8`) is essentially guaranteed by p_unk = 0.449 unless the Latin component carries information; it is a valid falsification test for the cipher but a near-certain "pass" for the null. It should be reported with that caveat (and ideally the learned-weight variant), not as a 0.8-bit victory of content-free models.

### 3.4 Other links checked
- **Parameter-count inflation:** M5's 291 k "params" are mostly the A×U×U two-unit channel table (24×33×33 ≈ 26 k) plus the Latin bigram table counts (≈ 240 k, fit on Latin, not on Voynich). Comparing this to M2's 67 k is not meaningful in either direction; neither side should cite parameter counts as evidence.
- **"Reproduces y→q / line-final m":** the pass thresholds (q-after-y ≥ .55 & otherwise ≤ .35; m-share ≥ .45 / ≤ .12) were chosen after the real values (.630/.264; .611/.066) were known, and M3-cond/M2-cond condition on *exactly* the two variables that define the statistics. Reproduction is therefore by construction — WS-C itself says "a description, not a mechanism". The informative part is that the *cipher* models cannot reproduce them (they have no access to those variables either, so this too is partly by construction). I downgrade this from evidence to a consistency check.
- **Lexicon size V = 1000 / channel K = 30:** Test B raised K to 60 with no qualitative change; V was not raised (cost). p_unk = 0.45 at V = 1000 means 55 % of Latin tokens are in-lexicon; a larger V lowers p_unk and *raises* the fixed penalty, so the reported V = 1000 is, if anything, the configuration most favourable to M5 under the fixed-prior design.

---

## 4. Garden of forking paths — statistics selected after seeing data

| WS | Statistic / choice | Selected post hoc? | Correction applied? | Risk |
|---|---|---|---|---|
| A-M1 | Top-K cross-boundary pairs merged, K ∈ {1,3,6}; PMI threshold count ≥ 100 | yes (pairs chosen from data) | no | low — result is null in all K |
| A-M1 | EVA unit inventory (12 digraphs) inherited from round 1 | pre-specified | — | low |
| A-M2 | MINC = 40 chosen after `m2_tune_control.py` (3 configs, killed at 600 s) | yes | no | low — reported as underpowered either way |
| A-M3 | 5 transpositions, best-of reported alongside identity | all reported | n/a | low |
| A-M4 | 10 candidate (unit,position) rules + 43 placebo pairs; z per rule | candidates pre-named; z not corrected for 43 comparisons | no | none in practice (no positive) |
| A-M4b | 7 deletion sets | exploratory | no | low |
| B-M1 | 9 corpora × 4 encodings; "best RMS z" reported as the minimum | exhaustive, all shown | n/a | low |
| B-M1 decoder | 5 LMs × folds 0,1 × {units, chars}; ranges reported | all shown | n/a | low |
| B-M2 | 2⁷ = 128 rule sets; min/max reported | exhaustive | n/a (reported as 1/128) | low |
| B-M3 | BPE inventory 80 chosen (MDL did not pick) | yes | no | low — negative |
| B-M4 | K ∈ {1,2,4,6,8}; chars vs units; Currier B separately | yes (grid) | no; max z = 1.86 among ~12 cells is *not* significant anyway | low |
| C | λ ∈ {0.6, 0.8, 0.9} evaluated on dev folds; best rows ranked | yes | no | low (0.04-bit range) |
| C | "reproduces" thresholds (.55/.35, .45/.12) set after seeing real values | **yes** | no | medium — turns a continuous PPC into a pass/fail by construction (§3.4) |
| C | 19 models ranked on dev; same dev folds then frozen for pre-registration | yes | n/a | medium — expected; blind set exists for this reason, but see §1.3 |
| C | Positive control run 4× with changing V / iters / UNK order until margin positive (`logs/run_cipher_control.log`: 24.07, 20.17, 18.76) | **yes** | no | medium — the control is a *demonstration* that a configuration exists, not a pre-specified power estimate |
| D | H-deg glyph progression: max over 10 glyphs | yes | **yes** (max-stat null, familywise p = 0.27) | handled |
| D | H-deg / H-copy / H-decan: 2 similarity measures each, both reported | yes | no (all null) | low |
| D | Register effect: 3 statistics (JS, ot/ok, q-rate), 2000 reps | yes | no; JS and ot/ok survive Bonferroni (p ≤ 0.0005 × 3) | low |
| D | Positive controls (numeral rings, self-citation chain) built with 30 % noise / one edit | parameters chosen by author | — | power is demonstrated only for those effect sizes |

Multiple-comparison correction was applied in exactly one place (WS-D glyph progression). Elsewhere it is immaterial because the results are null or the effects are p ≤ 0.0005 with ≤ 3 tests.

---

## 5. Certification

**CERTIFY** (replicated or audited; verdict stands)
- WS-A M1: EVA spaces are not random/fixed-interval; cross/within MI ratio 0.10–0.16 vs 0.06–0.19 (true) / ≈1.0 (independent). Replicated to 3 decimals. *Caveat added:* a non-random boundary rule that is not word-level (syllable-like) gives 0.32, so the test supports "genuine unit boundaries", not "word boundaries".
- WS-A M2, M3, M4: UNSUPPORTED verdicts (methods fail own controls / no positive gain). Audited, not re-run.
- WS-B M1 encoder: FALSIFIED (vowel deletion floor h2 2.89–3.22; marker variants destroy slot structure). Replicated.
- WS-B M1 decoder key-instability argument, M2 (abbreviation raises h2), M3 and M4 "no power" verdicts. Audited.
- WS-C conditioning gain of 0.24–0.30 bits/word from {prev-word last glyph, line-last}. Replicated.
- WS-C scrambled-lexicon null: Latin lexicon ≈ scrambled lexicon (−0.02; −0.035 at 4× budget). Replicated and strengthened.
- WS-D register effect: zodiac labels differ from same-page circular text in first-glyph distribution (JS 0.139, permutation p = 0.0005; present on all 3 usable leaves). Replicated with a stricter null. Structural only.
- WS-D H-deg/H-copy/H-decan/H-star: UNSUPPORTED. Audited.

**DOWNGRADE**
- WS-C headline "content-free models beat cipher models by ≥ 1 bit/word on every fold" → **restate** as "the Latin lexicon+channel component contributes ≈ 0 bits/word (learned weight 0.5 %) vs ≈ 0.9 bits on a true verbose cipher". The 0.8–1.1-bit margin is the fixed p_unk prior (§3). Same scientific conclusion, different (and more defensible) number.
- WS-C "content-free models reproduce y→q and line-final -m; cipher models do not" → consistency check by construction, thresholds post hoc (§3.4). Not independent evidence.
- WS-C positive-control margin (0.07 bits) → the correct effect size is ≈ 0.93 bits for the lexicon component; the control is adequate for the restated claim but was obtained after three configurations (§4).
- Pre-registration P1 → near-tautological under the fixed prior; report alongside the learned-weight comparison. P3–P6 → "generalisation to untouched leaves of effects already measured on those leaves in round 1", not out-of-sample prediction (§1.3).

**REJECT**
- Any reading of round-1 `REPORT.md` / ledger H2–H10 statistics as "held-out": they were computed on the full corpus including the now-blind leaves. (Not claimed explicitly anywhere, but the blind challenge framing invites it.)
- Parameter counts as evidence for or against M5 (291 k is dominated by Latin-side tables).
- No semantic claim exists in any workstream to reject; none was made.

---

## 6. Single biggest methodological risk in the program

**The blind set is blind to the code, not to the hypotheses.** `HOLDOUT.json` was frozen at 03:03 after round-1 analysis (02:42) had already measured, on the full corpus including leaves 24, 33–40, 72, 80, every structural regularity that round 2 then modelled and pre-registered (h2 ≈ 2.1, slot-grammar coverage, y→q, line-final -m, label register). Combined with the WS-C fixed-prior artefact, the pre-registered blind challenge is at risk of "passing" six predictions of which P1 is arithmetically near-certain and P3–P6 are generalisation checks of known facts. The blind evaluation remains valuable as a guard against *over-fitting of the fitted models*, but it cannot be presented as independent confirmation of the structural hypotheses. The fix for future rounds is procedural: freeze the holdout before any exploratory analysis of the transcription, and pre-register effect sizes that were not already observed on the held-out leaves.

A close second: the fixed `p_unk` design in M5/M6 (§3), which converts a mixture prior into a reported likelihood margin. It did not change the conclusion here, but the same design error in a case where the lexicon component was *weakly* informative (say 0.3 bits) would have reported the cipher as losing by 0.5 bits when it was in fact winning.

---

## 7. Files
- `e_common.py` — independent loader (blind filter + assert), EVA units, MI, h2.
- `rep_a_mi.py` → `logs/rep_a_mi.log`, `logs/rep_a_mi.json` (claim a; plus syllable-space variant).
- `rep_c_abjad.py` → `logs/rep_c_abjad.log`, `.json` (claim c; 8 languages × 4 encodings; Voynich per-fold h2).
- `rep_d_register.py` → `logs/rep_d_register.log`, `.json` (claim d; two nulls; leaf-level check; WS-D label definition cross-check appended).
- `rep_b_wsc.py` → `logs/rep_b_wsc.log`, `.stdout`, `.json` (claim b on folds 0,1; break tests A, B, C).
- `break_a2_learned_punk.py` → `logs/break_a2.log`, `.json` (train-learned UNK weight).