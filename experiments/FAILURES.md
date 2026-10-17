# Negative and void results (protocol v1 section 5)

## E002 (2026-10-15): structure models, posterior predictive checks
- P5 (label ot/ok/op/of-initial share >= 0.55) FAILED for every frozen generator (KN4+variety 0.12, TF d160+variety 0.13),
  vs DEV and vs LOCKED_TEST. The models are prose-only. DEV labels themselves sit at about 0.41.
- P1 and P2 FAILED vs DEV for the best-predicting model (TF d160+variety): it exaggerates y->q (OR 6.68 vs CI [4.09, 5.72])
  and line-final m/iin (OR 30.3 vs CI [12.2, 29.7]). Both passed vs LOCKED_TEST because that CI is wide (15 leaves).
- The masked-objective Transformer head was not implemented (optional in the brief).
See experiments/results/e002_ppc.json and reports/STRUCTURAL_FINDINGS.md.

## E003 (2026-10-15): classical solver solver-v1 on known-answer benchmark v1 (checkpoint sha256 690ab0a5...)
Single frozen run; no change was made after test results were seen (no protocol deviation). A 2-task-per-split
pipeline smoke run (`--limit 2`, 14 test tasks) was executed before the full run to check the script; its outputs
were deleted and nothing was changed afterwards.
- Gate 1 PARTIAL -> every train family is VOID for Voynich use: test_in mean char acc mono 0.83, homophonic 0.82,
  nulls 0.70, vigenere 0.65, columnar 0.52 (threshold 0.90). Failures concentrate at 300-char plaintexts
  (vigenere 0/6 solved, columnar 2/12) and in wrong language selection.
- Gate 2 FAIL for held-out encodings: test_enc char acc 0.063 (ratio 0.09; only boundary_noise partly solved, 8/140),
  test_both 0.111 (ratio 0.16). Family-ID accuracy is 0 by construction (held-out labels are never predicted).
- Gate 2 FAIL for 'language not in library' (R2, train-family LMs only): test_lang 0/120 solved, test_both 0/140.
  (R1 test_lang PASSES, ratio 0.97, because every test language has its own ref-book LM in the R1 library.)
- Gate 3 FAIL: decoy false-discovery rate 0.0625 (5/80) > 0.05; all 5 are `markov` decoys (5/13 = 0.38): order-2
  resamples of real ciphertext decode to locally fluent text that the calibrated confidence accepts
  (confidences 0.63-0.99). autocopy, grille, zipf_bag, one_time_pad, short_mono: 0 false discoveries.
See experiments/results/e003.json and e003_rows.jsonl.

## E008 linb: NeuroDecipher Linear B reproduction FAILED (2026-10-15)
- Result: primary metric (flow, edit=True, cap 1) 0.0% final, 0.87% best-over-epochs vs paper 84.7% (919 lost words; chance ~0.1%). 403.6 s, ran alone.
- Upstream ships NO Linear B config; our hyper-parameters (5 rounds x 60 epochs, capacity 1, charset 100, momentum 0.9) were guessed overrides on UgaHebSmallNoSpe. Cannot distinguish "wrong settings / undertrained" from "port bug" with this run alone.
- Patches reviewed: ortools min-cost-flow port is a 1:1 API rename (cost scaling `dists*100 -> int64` is upstream); numpy ragged-array fix reproduces numpy<1.24 behaviour. No bug found yet.
- Discriminating test: uga_small with the RELEASED upstream config (running). If it approaches 65.9%, port is fine and Linear B settings are the issue; if near chance, the port is broken.
- Status: NOT a valid positive control. Not used for any claim.
- **Update (21:18): discriminating test resolved.** uga_small with the released upstream config: primary metric 73.3% final
  (paper 65.9%), 2609.7 s. Port is functional. Caveat: upstream evaluates on the cognate-bearing words of the same 10% file,
  so this is not a strict like-for-like with the paper. Accuracy was ~0 for the first 50 epochs and only rose after
  epoch ~170, so the linb run (300 epochs total, guessed settings) is most likely undertrained. Next: rerun linb with
  the Ugaritic schedule (10 rounds x 150 epochs) before drawing any conclusion.

## E004: LLM hypothesis agent does not beat exhaustive search (2026-10-15)
Run `e004_20261015_211844`, 89 tasks x 4 modes, sonnet, 156 LLM calls, ~$3.00, 2h05m, 3 workers.

| mode | test_in (n=15) | test_enc (n=28) | test_both (n=28) | test_null FDR (n=18) |
|---|---|---|---|---|
| none | 0.667 | 0.107 | 0.107 | 0.111 |
| random | 0.667 | 0.143 | 0.179 | 0.111 |
| llm | 0.667 | 0.250 | 0.286 | 0.111 |
| exhaustive | 0.667 | 0.214 | 0.286 | 0.111 |
(solved rate; FDR = decoys/nulls wrongly "solved")

- Mechanism search helps on unseen encodings (none 3/28 -> llm 7/28), but the LLM matches exhaustive enumeration of the
  same op library (7 vs 6 of 28 on test_enc, 8 vs 8 on test_both). Differences of one task are not significant at n=28.
  Conclusion: the LLM adds no measurable value over brute force on this library; the bottleneck is the op library itself.
- Gate 3 FAILS in every mode: null FDR 2/18 = 0.111 > 0.05. Identical across modes, so it is the base solver's
  abstention, not the agent. (E003 had 0.0625 on a different null set.)
- An earlier E004 run (e004_20261015_192214) was killed by a system hang at ~115 traces; its partial files are not used.

## E005 (2026-10-16): solver v2 self-null abstention -> Gate 3 PASSES (fixes E003 failure)
v2 = v1 + abstain unless the answer beats scrambled-text ("self-null") re-solves by a margin. Margin 0.0051 set on
tune-family ciphers only (85 answered, 78 correct; 5th percentile of correct gaps). No decoys used for calibration.
v2 was created after seeing E003's Gate 3 failure, so this is a new version, not a retroactive fix; v1 numbers stand.

| split | v1 (E003) | v2 (E005) |
|---|---|---|
| test_null FDR (n=80) | 0.0625 (5/80) FAIL | **0.0125 (1/80) PASS** (the 1 is a markov decoy) |
| test_in solved (n=120) | 0.700 | 0.692 |
| test_lang R1 solved (n=120) | 0.667 | 0.633 (Gate 2 ratio 0.937, PASS) |

Gate 1 still PARTIAL (no family reaches 0.90 char acc; all VOID for Voynich), unchanged by abstention. Wall 43 min, 4 workers.
Note: E004's agent modes used v1 abstention; their 0.111 null FDR predates this fix.

## E008 linb_long (2026-10-16): Linear B still fails with the full schedule -> undertraining ruled out
- linb_long = linb with only the schedule changed to the Ugaritic one (10 rounds x 150 epochs): primary metric 0.33% final,
  1.31% best-over-epochs (paper 84.7%; chance ~0.1%). 1995 s, ran alone. The curve never leaves the noise floor.
- Ruled out: undertraining (this run); charset mismatch (all 70 Linear B signs and 28 Greek letters in the data are in the
  registered `minoan`/`el` charsets, 0 unknown tokens); port bugs (uga_small reproduces at 73.3%).
- Most likely cause: the paper's Linear-B-specific components (regulariser Omega_2, random restarts) are absent from the
  released code, so the released code cannot reproduce the Linear B result as shipped. Not pursued further (would mean
  re-implementing unreleased method details from the paper text).
- Status: Linear B is NOT available as a positive control. Ugaritic (uga_small) is the only validated real-script control.

## E009 (2026-10-16): Neural decipherer v1 (Qwen2.5-0.5B + LoRA, SFT and SFT+GRPO) solves nothing -> negative
- Operating point (calibrated abstention): both variants abstain on 100% of test tasks -> char acc 0.0 and solved 0/N on
  test_in, test_lang, test_enc, test_both. The calibrator was fitted on 250 tune-role dev tasks of which **0** reached
  char acc >= 0.9, so no threshold met the 0.95 selective-precision target and the operating threshold is "never answer".
  Gate 1 PARTIAL (every family VOID), Gate 2 FAIL on all three axes, Gate 3 PASS **trivially** (FDR 0/80 because it
  never answers; not evidence of good abstention).
- Forced-answer diagnostic (same decodes, never abstain; scored through vcl.eval.score.evaluate): char acc
  SFT 0.259 / 0.208 / 0.205 / 0.182 and SFT+GRPO 0.258 / 0.203 / 0.256 / 0.211 on test_in / test_lang / test_enc /
  test_both, vs a no-learning frequency-rank baseline 0.222 / 0.192 / 0.200 / 0.190. The network learned little beyond
  frequency analysis. Forced null FDR 0.84: the one_time_pad abstention training did not transfer (the model never
  emitted '<fam:noise>' on dev noise tasks either).
- Training failures along the way (all before any test number was seen):
  * SFT attempt 1 (lr 3e-4, left-padded prompts, no non-finite guard) diverged to NaN between steps 250 and 300
    (val token acc 0.17 at step 250). Replaced by v1 as run: right-padded prompts, aligned per-step cipher hint,
    <null> deletion token, lr 2e-4, skip-non-finite guard (3 steps skipped in 2900). Val token acc plateaued at 0.32.
  * E009 SFT eval attempt 1 was stopped during the dev stage to add the forced-answer diagnostic and to fix a dev-set
    construction bug (nulls and noise both on i%10==9 -> 25 tasks each); no test split had been scored.
  * GRPO attempt 1 (bf16 LoRA, lr 2e-5, micro-batch 8) degraded the policy within 40 steps (window reward -0.04 ->
    -0.63, sampled char acc 0.21 -> 0.13); stopped. Attempt 2 (fp32 LoRA master weights, lr 5e-6) is the reported one:
    204 steps, window reward 0.00 -> 0.07, sampled char acc 0.235 -> ~0.27, but noise-abstention fell 0.017 -> 0.
- Status: negative result. Not a basis for any Voynich claim. See reports/NEURAL_DECIPHERER.md, experiments/results/e009.json.

## E010B (2026-10-17): pre-registered zodiac month-name (H1) and day-label (H2) tests -> both negative (with limits)
Prereg `reports/E010B_PREREG.md` (sha256 dfb39b9e...8597, written 06:35Z before any statistic; unchanged; disclosure:
label lists had been viewed while building the anchor dataset). Leaves 70-73: none LOCKED_TEST. 299 labels counted
(30 / 15+15 / f72r2 29), matching voynich.nu.
- H1 (month name in Voynichese near the annotation; predicted pairs = 2 same-month + 6 '-bre' pairs): T1 p=0.19
  (z=1.0), T1/N2 p=0.17, T2 p=0.24, search-corrected T3 p=0.35. None survives Holm (alpha 0.01).
  The best single word-choice looks "significant" (p=1e-4, z=8.0) ONLY against random selections, i.e. before
  correcting for the search: a worked example of how searching manufactures anchors.
  Power (synthetic, same structure): mono 0.75-0.97, but homophonic/verbose 0.01-0.11. So H1 is negative only
  for one-glyph-per-letter spellings of the month names; against homophonic/verbose spelling it is uninformative.
- H2 (labels are day labels): exact recurrence O=34 vs within-zodiac shuffle 40.3 (p=0.96); ordered alignment A
  BELOW shuffle (z=-3.6, p=0.9999): labels are more alike within a page than across pages (page-level style, cf.
  forum reports of per-folio prefix drift), the opposite of a repeated day sequence. Power of A/Nb = 1.0 for all
  mechanisms -> negative. A vs other-section labels (Na) is significant (z=6.9) but Na fires on 99-100% of
  structure-free synthetic controls in 5 of 6 mechanism x language cells (0.10 in verbose/la): a style
  confound, predicted in the prereg -> not evidence.
- Note: the N2 null for T1 is slightly anti-conservative on controls (false-positive rate 0.03-0.05 at alpha 0.01).

## E011 (2026-10-17): Voynich twins -> NO TWIN (no family reaches Voynich's own variation)
- Five mechanism families (Naibbe-style verbose homophonic cipher, abbreviation, syllabary over 8 languages;
  Rugg grille and Timm-Schinner self-citation as meaningless decoys), 900 evals per family x language (decoys 2,700),
  fitted to DEV-only Voynich fingerprint (14 blocks of ~12k symbols). Best re-evaluated fit distance 2.11
  (naibbe/it) vs Voynich leave-one-block-out noise floor 0.99 (p90 1.29); Currier A-vs-B distance is 1.43.
- Every family misses low h_cond (z +1.8 to +4.5), rare word types (type_hapax) and the line-position effects
  (y->q, line-final m), which none has a mechanism for. Abbreviation fails on word length (z +11).
- Held-out ranking: Naibbe-style beats Rugg robustly (p 7e-8) and self-citation only without type_hapax (p 8e-8;
  with it p 0.018) -> automatic verdict "mixed". The meaningful-vs-meaningless classifier does not transfer across
  mechanisms (leave-one-family-out AUC 0.0), so its Voynich output is not used.
- Process note: first run's English-contamination filter contained "to" (common Czech word) -> 0 cs/ref chunks;
  fixed and final eval/analysis rerun with --reuse-search (same searched parameters). Both ledger row sets kept.
See reports/VOYNICH_TWINS.md, experiments/results/e011.json.

## E010 (2026-10-17): semantic-anchor power analysis -> the real anchor set is INSUFFICIENT
Known-answer simulation (de/fr/pl tune books; mono / verbose homophonic / flexible-anagram; 200 optimised wrong-key
fits per cell). Distinguishing the true key from keys optimised on wrong anchors needs N>=3-5 at r>=0.8 (mono),
N>=10 at r>=0.8 (verbose), N>=20 at r>=0.8 (flexible); at r<=0.3 not reached by N=40 except mono T2 (N=20).
Real set: 5 usable tier-B + 67 tier-C word-level anchors (no tier-A word-level; tier D L0 only, locked). Power at
plausible reliabilities is ~0 (best case mono rB=0.4/rC=0.15: 0.53); sufficient only if tier B >=0.8 reliable AND
mechanism is simple substitution with known segmentation and plaintext form. Random-key comparisons are passed
almost always and are therefore not evidence. See reports/ANCHORS.md, experiments/results/e010.json.

## E010C (2026-10-17): zodiac month names are NOT written with Greshko's Naibbe tables (pre-registered, negative)
Prereg `reports/E010C_PREREG.md` (sha256 280c500f..., written 08:32Z before any Voynich matching, read-only).
For each of the 12 zodiac pages, searched the ring text for runs of >= 2 consecutive words that are valid Naibbe
encryptions (published tables) of consecutive letters of the page's month name. Own-month score is 0 on all 12
pages (no 2-word run anywhere); T = -0.17, p = 1.0 (10k permutations). Positive control (true encryption inserted):
power 1.00; false-positive control (wrong month inserted): 0.00. Verdict NEGATIVE.
Scope: rules out only the specific hypothesis "month names enciphered with Greshko's 2025 tables". It does not test
other verbose-homophonic tables (the tables are a modern reconstruction). Labels were not tested (one Naibbe word
encodes only 1-2 letters).
