# Voynich AI Cryptolinguist — full local research handoff

This package contains **every file currently available in the ChatGPT working directory at handoff time**, unmodified in `source_dump/`, plus a master Claude Code prompt, evidence context, manifest and starter smoke tests.

**Do not confuse the user-reported external Codex/Claude findings with attached repositories.** Their original code/logs were not supplied in this chat and must be imported separately.

## Quick start
1. Unzip this archive into a dedicated project folder.
2. Open Claude Code in the project folder.
3. Give Claude Code the contents of `CLAUDE_CODE_MASTER_PROMPT.md` and tell it to execute, not summarize.
4. Before new model development, run:

```bash
python tools/verify_manifest.py
python -m unittest discover -s tests -v
python tools/synthetic_baseline.py
```

5. Supply the complete Codex and Claude repository outputs from the later runs when available.

## Contents
- `source_dump/`: full locally available source files, including the original IVTFF DOCX, older Python scripts, experiment ZIPs, CSVs, reports and images.
- `MANIFEST.json`: SHA-256 inventory for all source files.
- `RESEARCH_CONTEXT.md`: results, limitations, missing evidence, and warnings.
- `CLAUDE_CODE_MASTER_PROMPT.md`: full autonomous coding/research assignment.
- `tools/verify_manifest.py`: file-integrity check.
- `tools/synthetic_baseline.py`: standard-library toy positive-control substitution experiment; **NOT a trained decipherment model**.
- `tests/`: smoke tests.

## Why this approach
A small Voynich language model can learn the text's statistical structure, but that does not supply semantic labels. This project instead trains and evaluates decipherment *methods* on externally verifiable problems, with unknown-language and impossible-task controls, and uses them to generate falsifiable Voynich hypotheses.
