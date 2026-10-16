# Neural decipherer v1 (E009): negative result

**Verdict.** A Qwen2.5-0.5B model fine-tuned with LoRA (SFT, then SFT + GRPO) **solves no benchmark task** on any
split. That includes held-out encoding families, the question this milestone was meant to answer. At the calibrated
operating point it abstains on everything. Forced to answer, it is only slightly better than plain
frequency analysis. Gate 2 (held-out-family transfer) **FAILS** on every axis for both variants.
**No decipherment.** None of this is a basis for any Voynich claim.

Source of truth: `experiments/results/e009.json`. Per-variant detail: `e009_sft.json`, `e009_grpo.json`, and the
`*_rows.jsonl` files. Training logs: `e009_sft_log.jsonl`, `e009_grpo_log.jsonl`, `e009_grpo_attempt1_log.jsonl`.
Failures: `experiments/FAILURES.md` (E009).

## Method

| part | choice | why |
|---|---|---|
| base model | Qwen2.5-0.5B (HF rev `060db649…`), frozen bf16, MLX | fits in 16 GB with room to spare; MLX runs on the M5 GPU |
| adapters | LoRA rank 16 on every attention/MLP projection of all 24 blocks, plus trainable cipher-id embedding, feature projection, special-token rows and output bias (8.9 M params) | |
| input | relabelling-invariant: frequency-rank ids computed over the **whole task** (Aldarrab & May 2021) plus 15 symbol-profile features per position (log frequency; word-initial/final/single/doubling rates; left/right-neighbour entropy and variety; task-global length, inventory, boundary flag, mean word length). Fed as `input_embeddings`, bypassing the BPE tokenizer. Tested invariant to glyph renaming (`tests/test_neural.py`) | |
| windowing | 256-symbol windows, ranks and features shared across all windows of a task | |
| output | restricted vocabulary: 133 train-family letters, reusing Qwen's frozen tied embedding rows, plus specials. Step 0 emits a family token (`<fam:noise>` = abstain). Then exactly one token (letter / space / `<null>`) per cipher symbol. Answer step t also receives the embedding of cipher symbol t (an "aligned hint"), so the model is a tagger with autoregressive LM context | this hypothesis class is 1:1 symbol→token with deletion: it covers every TRAIN encoding but not 1:many or many:1 mechanisms (verbose, syllabary, nomenclator) |
| aggregation | `concat` (window outputs joined) or `vote` (majority output per glyph over the whole task, i.e. one global key), picked per predicted family on dev tasks | |
| abstention | (a) the MIN_LETTERS=60 prior, as in solver v1; (b) a logistic calibrator for P(char acc ≥ 0.9) over decode-quality features, threshold = the smallest one whose out-of-fold selective solved rate is ≥ 0.95, as in v1; (c) the solver-v2 self-null test (decode an order-2 resample of the task's own ciphertext; margin = 5th percentile of correct dev gaps) | |
| SFT data | fresh tasks from **ref**-role books, train language families × train encodings, plus 8% one_time_pad noise windows (target: abstain). 23,200 windows | |
| GRPO data | same generator and roles, different seed, 10% noise | |
| dev / calibration | 250 tasks from **tune**-role books (unseen documents), same seed for both variants | |
| decoys | none, anywhere | |

**Leakage rules followed.** Nothing in `vcl.neural` reads `benchmark_v1/secret/`, test-role books, held-out
language families, held-out encodings or the decoy generators. `data.books_for` asserts that the role is ref or tune
(tested). Secrets are read only through `vcl.eval.score.evaluate` at final scoring. Abstention training used
one_time_pad-style noise streams generated here; no decoys were used.

**GRPO is genuine on-policy RL.** We wrote a minimal loop. We did not use mlx-lm-lora, because its GRPO expects
tokenised text prompts and the stock LM head, and this model takes custom rank/feature embeddings. Each step:

- Sample 4 windows × G=6 outputs from the **current** policy (temperature 1, same constrained decoding as inference).
- Score them with our own copy of the scoring logic (`vcl.neural.reward`; the test checks it matches
  `vcl.eval.score.char_acc`). Reward = char accuracy vs the known plaintext, −0.25 if accuracy < 0.3, +1 for
  abstaining on noise, −0.5 for answering noise, −0.5 for degenerate output, +0.1 for the right family token.
- Normalise advantages within each group. Policy-gradient step (one update per batch, so PPO ratio = 1), Dr.GRPO-style
  constant length normaliser, no KL term, AdamW lr 5e-6, fp32 LoRA master weights.

## Results (full test splits, no subsetting)

Char accuracy (Gate 2 metric), solved rate in parentheses. Operating point = what the protocol scores.

| split | solver v1 R1 (E003) | solver v1 R2, train-lang LMs only | solver v2 (E005) | freq-rank, no learning | **SFT** operating | SFT forced (diag.) | **SFT+GRPO** operating | SFT+GRPO forced (diag.) |
|---|---|---|---|---|---|---|---|---|
| test_in (n=120) | 0.708 (0.700) | – | 0.692 (0.692) | 0.222 (0) | **0.000 (0)** | 0.259 (0) | **0.000 (0)** | 0.258 (0) |
| test_lang (n=120) | 0.688 (0.667) | 0.001 (0) | 0.648 (0.633) | 0.192 (0) | **0.000 (0)** | 0.208 (0) | **0.000 (0)** | 0.203 (0) |
| test_enc (n=140) | 0.063 (0.057) | – | – | 0.200 (0) | **0.000 (0)** | 0.205 (0) | **0.000 (0)** | 0.256 (0) |
| test_both (n=140) | 0.111 (0.079) | 0.000 (0) | – | 0.190 (0) | **0.000 (0)** | 0.182 (0) | **0.000 (0)** | 0.211 (0) |
| test_null FDR (n=80) | 0.0625 | – | 0.0125 | 1.0 | **0.000** | 0.84 | **0.000** | 0.84 |

- "Forced (diag.)" uses the same decodes but never abstains, scored through `vcl.eval.score.evaluate`. It is a
  diagnostic, not an operating point. "freq-rank" maps glyph rank k to the k-th most frequent train-language letter
  and always answers.
- Char accuracy here is 1 − edit distance / length. Even an unrelated decode scores about 0.2 just by getting the
  spaces right, so forced accuracies around 0.2 mean "no decipherment".
- Like-for-like on test_lang and test_both: the neural model only ever saw train-family letters and cannot emit
  Greek, Hebrew or Telugu characters. The fair solver comparison there is v1 **R2** (train-family LMs only), which
  also scores ≈ 0. R1 had an LM for every benchmark language.
- Solver v2 was not run on test_enc or test_both in E005.

### Gates (from `vcl.eval.gates`, quoted from e009.json)

| gate | SFT | SFT+GRPO |
|---|---|---|
| 0 reproducibility | PASS | PASS |
| 1 positive control (≥ 0.90 per family) | PARTIAL: all five families VOID (0.0) | PARTIAL: all VOID |
| 2 test_lang / test_enc / test_both | FAIL / FAIL / FAIL (0/120, 0/140, 0/140 solved) | FAIL / FAIL / FAIL |
| 3 nonsense controls | PASS, FDR 0/80, **trivially** (never answers anything) | PASS, **trivially** |

Gate 2 on the forced diagnostic also fails on every axis. The out-of-family/in-family ratios are high (0.70–0.99),
but only because in-family accuracy is itself at the floor; 0 tasks are solved and p vs random key ≈ 1.

### Held-out encoding transfer
**No transfer.** Forced char accuracy on test_enc is 0.205 (SFT) and 0.256 (GRPO), against 0.200 for pure frequency
analysis. Zero held-out-encoding tasks are solved. That is worse than solver v1, which solves 8/140 on test_enc
(mostly boundary_noise). GRPO's gain on test_enc comes almost entirely from `verbose` (0.04 → 0.27 forced). That looks
like its outputs moving towards generic letter statistics, not any decipherment: abjad, autokey and reversed_words
all stay at about 0.27.

## What RL actually changed
- On the training distribution (sampled windows, ref books): mean window reward went from 0.00 (first 50 steps) to
  0.055 (last 50), and sampled char accuracy from 0.235 to about 0.27.
- On greedy decoding of dev tasks it changed almost nothing: mono 0.33 → 0.31, nulls 0.25 → 0.29, columnar
  0.10 → 0.13, still 0 solved. In-family forced test accuracy is unchanged (0.259 → 0.258).
- It **removed** abstention: sampled noise-abstention fell from 0.017 to 0, and family-ID accuracy on test_in fell
  from 0.50 to 0.275. The +1 abstain reward on 10% noise prompts was outweighed by the char-accuracy term, which a
  generic letter-frequency output can partly collect on noise windows as well. This is a reward-design flaw.
- Attempt 1 (bf16 LoRA, lr 2e-5) actively degraded the policy within 40 steps and was stopped; details in FAILURES.

## Failure modes
1. **SFT plateau at about frequency-analysis level.** Validation token accuracy reached 0.32 after 2,900 steps
   (23k windows, 62 min). Aldarrab & May-style models need orders of magnitude more data or compute before "clicking".
   The budget here (≤ 2 h per run on one M5) bought about 23k windows.
2. **Calibration found no solvable region.** 0 of 250 dev tasks were solved, so the protocol-correct operating
   point is "never answer". The Gate 3 PASS is therefore uninformative.
3. **Noise abstention never learned.** The model never emitted `<fam:noise>` on dev noise tasks, and forced FDR is
   0.84. The 8–10% noise share and a single family token at step 0 were not enough signal.
4. **Architecture limits** that would remain even with more compute:
   - one token per cipher symbol, so verbose, syllabary and nomenclator are out of reach by construction;
   - columnar can only be learned as substitution in cipher order;
   - no letters from held-out-family scripts.
5. **Numerical issues**:
   - bf16 LoRA with lr 3e-4 diverged (NaN at step about 270); a non-finite guard and lr 2e-4 fixed it;
   - bf16 LoRA is too coarse for RL-sized updates, so we moved to fp32 master weights for GRPO.

## Not done
- **Hybrid** (model proposes a key, solver v2 polishes): not built. With dev char accuracy at about 0.3, a seed key
  from this model is roughly a frequency-analysis initialisation, which solver v1 already uses.
- **Best-of-N**: not run. The RL above is genuine GRPO, so no non-RL substitute was needed.

## Compute
All jobs ran one at a time; peak MLX memory was ≤ 7.8 GB in training and ≤ 2.8 GB in evaluation.

| job | wall | peak MLX memory |
|---|---|---|
| profiling + smoke tests | ≈ 30 min | 13 GB in the fp32-LoRA probe, which led to switching to bf16 |
| SFT attempt 1 (NaN) | 11 min | 7.8 GB |
| SFT v1 | 61.7 min | 7.8 GB |
| SFT eval | 9 min (+ ≈ 6 min aborted attempt) | 2.3 GB |
| GRPO attempt 1 | ≈ 5 min | 7.8 GB |
| GRPO v1 | 35.2 min | 6.5 GB |
| GRPO eval | 14.8 min | 2.8 GB |
| **total** | **≈ 2 h 55 min** | |

Adapters (base weights not committed):

| file | size | sha256 |
|---|---|---|
| `checkpoints/neural_sft_v1.safetensors` | 18.2 MB, bf16 LoRA | `d160f979…6059` |
| `checkpoints/neural_grpo_v1.safetensors` | 35.8 MB, fp32 LoRA | `2e5a5d09…78bf` |

## Reproduce
```
uv pip install --python .venv/bin/python -e '.[neural]'
caffeinate -ims .venv/bin/python -m vcl.neural.train_sft --steps 2900 --minutes 65
caffeinate -ims .venv/bin/python -m vcl.neural.train_grpo --minutes 35 --steps 1000
caffeinate -ims .venv/bin/python experiments/e009_neural_decipherer.py --variant sft
caffeinate -ims .venv/bin/python experiments/e009_neural_decipherer.py --variant grpo
.venv/bin/python experiments/e009_neural_decipherer.py --freq-baseline
.venv/bin/python experiments/e009_neural_decipherer.py --combine     # also appends ledger rows
```
(Run with `PYTHONPATH=src` if the package is not installed.)
