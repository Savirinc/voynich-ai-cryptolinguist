# Missing external repositories and evidence (NOT imported)

These are cited in `data/raw/handoff/RESEARCH_CONTEXT.md` as **user-reported**. Their code, logs, splits and
outputs are not in this repository. Nothing below has been rerun here, and no code has been invented to stand in
for them. Each item should be imported into `external/<name>/` with its own commit hash before reuse.

| # | Missing item | Reported result (unverified) | What is needed to verify |
|---|---|---|---|
| 1 | Codex repo: Schechter Latin–Occitan glossary falsification | 89.2% coverage with 4,063 entries vs 89.4% for frequency-ranked arbitrary meanings; frozen decoder ~5% unseen-type coverage; 583/947 targets unattested; Latin bigram z=-0.47 vs line-shuffled | repo, glossary file + licence, held-out folio list, Latin/Old French reference corpora |
| 2 | Claude repo: negative cipher-family searches (mono/homophonic/polyalphabetic, abbreviations, abjads, transposition, nulls, allograph merges) | no validated decipherment; context-dependent & units-to-syllable searches VOID (failed own positive controls) | repo, search configs, positive-control logs |
| 3 | Claude repo: content-free conditioned char model | 11.01 bits/word on blind prose; P1–P4, P6 pass, P5 fail (48.6% vs >=55%) | exact split, tokenisation, scoring convention, checkpoint |
| 4 | Claude repo: reviewer corrections | 0.8-bit information gap invalidated as fixed-prior artefact | review log |
| 5 | Claude repo: botanical-source study (940 drawings, 6 manuscripts) | Tractatus positive control detected; f35v vs Latin 6823 not significant after correction | image set + licences, blind codings, permutation code |
| 6 | Held-out split hashes for all external results | — | split files + hashes |
| 7 | Veneto alchemical herbals, some manuscript scans | untested | institutional access |
| 8 | ChatGPT experiments with no local file (e.g. 001, 014-046 gaps, 054-056 partial) | see ledger in handoff | original files |

## Locally verified provenance gap found during reproduction
- `Voynich_Experiment_066_Context_and_Zodiac.zip`: the archived `results.json` contains 5 zodiac fields
  (`size_matched_*`, `sensitivity_note`) that the archived `voynich_experiment_066.py` does not produce. They were
  added by an unarchived step. See `experiments/repro/legacy_066_rerun.json`.
