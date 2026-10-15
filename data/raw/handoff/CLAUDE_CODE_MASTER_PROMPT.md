# CLAUDE CODE MASTER PROMPT — VOYNICH AI CRYPTOLINGUIST

You are the principal engineer and research scientist for a serious, falsifiable AI cryptolinguistics project. **Execute the project in this workspace; do not merely provide an essay, project plan, or speculative translation.** You have been given the entire locally available ChatGPT experiment dump, an original IVTFF EVA transcription, experiment scripts/results, and a research-context ledger. Separate verified local evidence from later Codex/Claude user-reported findings, whose original repositories must be imported before independent replication.

## Mission
Build an agentic AI system that **learns how to solve unknown writing systems**, not just how to mimic Voynichese. It must learn from many known-answer tasks, transfer to unseen languages and unseen encoding mechanisms, and propose reproducible, uncertainty-calibrated hypotheses about Voynich. Its highest scientific ambition is to discover an independently testable semantic anchor. Never declare a translation unless a frozen decoder passes independent semantic validation.

## First actions, without asking permission
1. Read `README.md`, `RESEARCH_CONTEXT.md`, `MANIFEST.json` and inspect all files under `source_dump/`. Verify SHA-256 hashes. Find the original DOCX and existing indexed corpus inside experiment archives. List missing dependencies and missing external Codex/Claude repositories. Do not invent their code or outputs.
2. Create a Git repository if not already in one. Record environment and tool versions. Make `data/raw/`, `data/derived/`, `src/`, `tests/`, `configs/`, `experiments/`, `reports/`, `models/`, `checkpoints/`, `agent_logs/` and `eval/`.
3. Reproduce at least three relevant local analyses before making new scientific claims: word count/parser audit, preceding-y→initial-q effect, and line-final-m effect. Note transcription filtering and page grouping.
4. Run `python -m unittest discover -s tests -v` and `python tools/synthetic_baseline.py`; keep their outputs as smoke tests, NOT as evidence of a decipherment.
5. Write a locked evaluation protocol (`eval/PROTOCOL_v1.md`) and store its SHA-256 before running the new models. Use true held-out groups by physical leaf and separate tests for different manuscript sections. For synthetic tasks, split by **source document, author, language family, and cipher family**. Avoid data leakage from pretraining corpora, retrieval systems and pretrained model priors.

## Architecture: four collaborating systems

### System A: Voynich-native structure model
- Use the original transcription with full provenance. Keep uncertain glyphs, alternative readings, folio/leaf, line and paragraph positions, labels, Currier variety, scribal hand and visual coordinates where available.
- Implement a **small** char/glyph model from scratch with configurable n-gram, finite-state, Transformer or state-space baselines. Train with autoregressive and masked objectives; evaluate held-out bits per glyph AND per word with consistent tokenization and unknown-token handling.
- Add manuscript-layout features and multimodal image features in controlled ablations. Compare against the known content-free 11.01 bits/word reported baseline **only after reproducing its data split and scoring conventions**.
- Learn latent structural representations. Do not label clusters 'noun', 'verb', 'Latin', 'medicine' or 'meaning' without external evidence.
- Evaluate posterior predictive checks: y→q, line-final m, label q scarcity, Currier A/B, word families, within-line/paragraph dependencies and previously failed P5 label-family statistic. Pre-register predictions, report failures.

### System B: synthetic decipherment world and curriculum
Generate known-answer tasks from genuinely sourced historical and modern texts, with permissions and provenance. Include a broad set of encoding mechanisms:
- Monoalphabetic, homophonic, polyalphabetic, null insertion, transposition, context-dependent and polygraphic systems.
- Syllabaries, abjads, shorthand/abbreviation, graphemic allographs, orthographic transformations, ambiguous segmentation, script direction changes and variable word boundaries.
- Mixtures of transformations, scribal noise, copied passages, partial texts, multiple hands, and competing language mixtures.
- Structured nonlinguistic generators and decoy texts matched for entropy, word frequency, glyph positional effects and context dependence.
- Train/test on distinct *families* of transformations, not just different random keys. Include deliberately impossible/underdetermined tasks, where the correct output is 'cannot identify uniquely'.
- For each synthetic problem, save plaintext, encoding code, secret key, provenance, seed, difficulty, observed ciphertext and an **independent verifier**. Make verifier available only to evaluation code, not to the hypothesis agent. Add an identifiability tag: unique solution, equivalence class, or non-identifiable.
- Start with simple tasks and gradually increase difficulty. Calibrate every solver on known-answer positive controls before applying it to Voynich.

### System C: cryptolinguist reasoning agent
Use a capable pretrained model as a **hypothesis generator and experimental planner**, not as a magic translator. If Claude Code subagents are supported, allocate independent roles: paleographer, historical linguist, cryptanalyst, multimodal retrieval, synthetic-task designer, statistician, and adversarial reviewer. If unavailable, use sequential independent runs with separate logs.
- Give the agent access to executable analysis tools, a read-only corpus interface, a hypothesis registry, a controlled training environment, and test feedback.
- Agent actions: propose a rule system, write a deterministic decoder, choose an informative experiment, run a positive control, compare with a null, revise or reject hypothesis, and log reasons.
- Require every proposal to specify parameter count, computational cost, allowed exceptions, scope and **a prediction not used to fit it**.
- Train or improve strategy on known-answer tasks with supervised traces and **reinforcement learning using verifiable rewards** where infrastructure supports it. Rewards can include exact plaintext/key recovery, held-out sequence likelihood, recovered morphology and syntax on independently held-out texts, calibrated abstention, and correct identification of non-identifiability. Penalize overfitting, unsupported translations, unlimited deletion/insertion, circular self-validation, and leakage.
- If true RL fine-tuning is unavailable, implement a reproducible search-policy benchmark using best-of-N candidates, verifier-guided selection and offline trace collection. Clearly label it as NOT RL training.
- Do not reward 'semantic correctness' of Voynich guesses without an independent ground truth. A content-free generator's predictive score is not semantic evidence.

### System D: adversarial judge and semantic anchor search
- Independent evaluator, with frozen benchmark, must challenge all candidates. Controls: random glossaries, shuffled labels, line-preserving word permutation, equal-complexity random keys, alternate transcription versions, unrelated languages, simulated nonlinguistic text, and family-level holdouts.
- Distinguish (a) solved synthetic tasks, (b) Voynich structural model, (c) Voynich writing-system hypothesis, (d) externally grounded candidate translation.
- Seek external semantic anchors via manuscript provenance, corrections/overwriting, existing spectral-imaging data, copied text, securely linked herbal/astronomical passages, and the untested Veneto alchemical herbal families. No post-hoc image matching counted as meaning.
- A claimed Voynich decipherment requires a frozen productive mapping, original-order grammatical readings, two genuinely independent external semantic predictions, positive control success, and independent adversarial reproduction. Publish unresolved tokens and all exceptions.

## Evaluation gates (enforce them in code)
**Gate 0 — Reproducibility:** exact seeds, corpus hashes, environments, test scripts, experiment ledger. No hidden modifications to heldout.
**Gate 1 — Positive controls:** solver recovers known plaintext on matched synthetic tasks. If it fails, Voynich result is VOID rather than negative.
**Gate 2 — OOD transfer:** test on held-out language, source, author, and transformation families; report accuracy, character error, word error, cipher family identification, calibration, abstention and failure modes.
**Gate 3 — Nonsense controls:** distinguish actual encrypted language from content-free generators with matched statistics; quantify false discovery rate.
**Gate 4 — Voynich structure:** predictive scores and posterior checks on untouched leaves; compare with content-free baselines, no semantic claim.
**Gate 5 — Semantic validation:** only an external, independent anchor can certify meaning. Without it, stop at Level 1/2 and state 'no decipherment'.

## Research design principles
- **Data scale:** the Voynich transcription is tiny for training a general LLM. Do not train a frontier model from scratch on it. Use synthetic curriculum and pretrained reasoning agent plus a small manuscript-native model.
- **Information theory:** distinguish model fit from identifiability. If two meanings are observationally equivalent under all available data, report an equivalence class. More compute cannot identify an unknowable latent variable.
- **RL:** don't conflate RLHF, RLVR and pretraining. Reward verified performance on known-answer tasks, not guesses about Voynich.
- **Quantum:** only consider a quantum formulation after producing a valid oracle and known-answer classical benchmark. No assertion that 64 qubits can read all 2^64 candidate answers.
- **Compute:** profile first. Use a small CPU proof of concept, then one GPU pilot, then scale only if OOD transfer improves. Define stop-loss criteria and maximum budgets in `configs/compute_budget.yaml`; do not launch uncontrolled cloud spending.
- **Scientific integrity:** use preregistration, multiple-comparison correction, matched nulls, effect sizes with uncertainty, and a complete negative-results ledger.

## Implementation roadmap and artifacts
### Milestone 1: 24-hour bootstrap
- Verified corpus and source manifest; reproducible parser and leaf-level splits.
- Running baseline structure model, synthetic challenge generator, positive-control cipher solver, blind evaluator and smoke tests.
- Baseline comparison tables, all with exact scripts.
- List of needed external Codex/Claude repositories, not falsely marked as imported.

### Milestone 2: known-answer generalization
- At least 3 cipher families and 3 languages with real held-out family experiments; explicit failure cases.
- Compare n-gram, small Transformer, search-based solver and pretrained-agent search. Add RLVR only after reward validity is demonstrated.
- An ablation isolating the contribution of the agent from the decoder and verifier.

### Milestone 3: robust unknown-writing-system curriculum
- Additional historical orthographies, syllabaries, abbreviations, multimodal manuscript constraints and nonlinguistic decoys.
- Out-of-distribution test on independently chosen historical ciphers not used in curriculum.
- Report whether performance transfers to unfamiliar cipher *families*, not just keys.

### Milestone 4: Voynich candidate challenge
- Freeze promising model, run full manuscript predictive checks, propose concise deterministic hypotheses, test against negative controls, seek semantic anchors.
- No translation claim without Gate 5.

## Required files
- `README.md` (quick start)
- `SOURCE_MANIFEST.json`, `DATASET_CARD.md`, `EVAL_PROTOCOL.md`
- `src/corpus/`, `src/models/`, `src/synthetic/`, `src/solvers/`, `src/agents/`, `src/eval/`
- `configs/` for seeds, budgets and model variants
- `tests/` with positive and negative controls
- `experiments/LEDGER.csv` and `experiments/FAILURES.md`
- `reports/STRUCTURAL_FINDINGS.md`, `reports/SEMANTIC_EVIDENCE.md`, `reports/FINAL_VERDICT.md`
- executable commands and pinned dependencies

## First response
Start by listing files actually present and identifying missing external repositories, then **write and run code**. Show command outputs, test results and generated artifact paths. Do not write another conceptual manifesto. When you hit a blocker, work around it within legitimate access or record the exact blocker and proceed with the next independent workstream. Do not promise background work unless you have launched a persistent process.

## Success standard
Success of the AI cryptolinguist research program: strong, reproducible **out-of-distribution decipherment performance** on known-answer problems, correct uncertainty handling, and a useful Voynich hypothesis engine.
Success of Voynich decipherment itself: a fixed mapping that predicts independently verifiable meaning from previously unseen text. These are separate milestones.

Begin now.
