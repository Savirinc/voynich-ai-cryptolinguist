# Voynich AI Cryptolinguist

An open, falsifiable research program to build an AI that **learns how to decipher unknown writing systems**,
trained and scored on known-answer problems (many languages × many encoding mechanisms × nonlinguistic decoys),
and only then pointed at the Voynich Manuscript (Beinecke MS 408).

> **Status: no decipherment.** Nothing in this repository is a translation of the Voynich Manuscript.
> Gate 5 (independent semantic validation) has not been passed. See `reports/FINAL_VERDICT.md`.

## Quick start
```bash
uv venv --python 3.11 .venv && uv pip install -e ".[dev,repro]"
.venv/bin/python data/raw/handoff/tools/verify_manifest.py        # handoff integrity (143 files)
.venv/bin/python experiments/e001_corpus_audit.py                  # parser + split + effect reproduction
.venv/bin/python -m vcl.synthetic.corpora fetch                    # rebuild plaintext corpora (hash-verified)
.venv/bin/python -m vcl.synthetic.benchmark                        # rebuild known-answer benchmark
.venv/bin/python -m pytest -q
```

## Layout
| Path | What |
|---|---|
| `data/raw/handoff/` | Unmodified ChatGPT-era archive (IVTFF DOCX, scripts, results) + SHA-256 manifest |
| `src/vcl/corpus/` | IVTFF parser with provenance, leaf splits, structural-effect statistics |
| `src/vcl/models/` | System A – Voynich-native structure models (n-gram, small Transformer) |
| `src/vcl/synthetic/` | System B – sourced corpora, 13 encoding families ("encrypt any language"), decoys, benchmark builder |
| `src/vcl/solvers/` | Cipher solvers, family classifier, abstention |
| `src/vcl/agents/` | System C – pretrained-LLM hypothesis agent (Claude via headless CLI) |
| `src/vcl/eval/` | System D – blind evaluator and code-enforced Gates 0–5 |
| `eval/PROTOCOL_v1.md` | Locked evaluation protocol (hash-checked by tests) |
| `experiments/` | Numbered experiments, `LEDGER.csv`, `FAILURES.md`, results |
| `reports/` | Findings, missing external evidence, final verdict |
