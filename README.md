# Voynich AI Cryptolinguist

**An open, pre-registered attempt to decipher the Voynich Manuscript (Beinecke MS 408). Every attack is proven
on known answers before it touches the manuscript.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Cite this](https://img.shields.io/badge/cite-CITATION.cff-green.svg)](CITATION.cff)

> **Status: no decipherment.** Nothing in this repository is a translation of the Voynich Manuscript. What it
> contains is validated tools, about 25 pre-registered experiments (null results included), and a hypothesis
> space that has been narrowed down step by step.
> **Start here: [`reports/SUMMARY.md`](reports/SUMMARY.md)**, a plain-language summary of everything done so far.

## Why another Voynich project?
Most failed Voynich "solutions" share the same flaws:
- no test on texts with known answers;
- no meaningless controls;
- words picked to fit;
- only part of the text read.

This project is built to make those failures impossible:

| Rule | What it means in practice |
|---|---|
| **Known answers first** | An attack must crack synthetic ciphers of its own class before it touches Voynich |
| **Controls** | Meaningless look-alike texts (Rugg grille, self-citation, shuffled letters) are attacked the same way; zero false claims allowed |
| **Pre-registration** | Each test's decision rule is written, locked read-only and sha256-hashed *before* the run |
| **Locked pages** | 15 leaves are held back for one final confirmation decode |
| **Everything published** | Every result, including every NO CLAIM, goes into [`experiments/LEDGER.csv`](experiments/LEDGER.csv) and [`experiments/FAILURES.md`](experiments/FAILURES.md) |

The full plan is in [`reports/METHODOLOGY.md`](reports/METHODOLOGY.md). It works through three doors: a known
language hidden by a system, an unknown language, or no language at all.

## What we have found so far
- **A validated attack on verbose homophonic ciphers** (E017). It cracked 8/8 synthetic texts, made 0 false claims
  in 32 controls, and identified the right language 8/8 times.
- **Run on Voynich with the published Naibbe tables, it returned NO CLAIM** (E018), and not narrowly.
- **Stage A tests narrowed the space** (E019–E025). Voynich words behave like word-sized units whose common words
  persist like grammar words. No glyph grouping looks like an alphabet, and the line is a functional unit.
  - *Ruled out (for the classes tested):* fixed-key letter ciphers, Rugg-style grilles, self-citation and
    syllabaries.
  - *Favoured:* a word-level codebook or a **compound stem + ending** notation.
- **Stage B in development.** On synthetic Latin, a two-step "endings first, then stems" attack decodes **98.8% of
  endings** and 53% of whole words. That is Kober's Linear B insight, turned into an algorithm.

## Quick start
Requires Python 3.11 and [uv](https://github.com/astral-sh/uv), or plain pip.
```bash
git clone https://github.com/Savirinc/voynich-ai-cryptolinguist && cd voynich-ai-cryptolinguist
uv venv --python 3.11 .venv && uv pip install -e ".[dev,repro]"
.venv/bin/python -m vcl.synthetic.corpora fetch      # public-domain plaintext corpora, hash-verified
.venv/bin/python -m pytest -q                        # test suite
```
**Try the validated attack in about a minute.** The demo encrypts a text with a fresh secret key, cracks it, and
applies the claim rule:
```bash
.venv/bin/python examples/known_answer_demo.py --lang it              # e.g. 93% letters, CLAIM
.venv/bin/python examples/known_answer_demo.py --lang it --control rugg   # meaningless control: NO CLAIM
.venv/bin/python examples/known_answer_demo.py --cipher my_words.txt --lang la   # attack your own cipher
```

## Use it for your own hypothesis
**The quest is open.** You can fork this, test your own theory with the same rules, and send us the result,
positive or negative. [`docs/USING.md`](docs/USING.md) covers:
- loading the transliteration (DEV leaves only);
- encrypting any text with any of the cipher families;
- building meaningless controls;
- running the validated attack and claim rule;
- adding a language corpus;
- writing and locking a pre-registration.

[`CONTRIBUTING.md`](CONTRIBUTING.md) explains how to submit a result.

## Repository map
| Path | What |
|---|---|
| `src/vcl/corpus/` | IVTFF parser with provenance, leaf splits, glyph-unit inventories |
| `src/vcl/synthetic/` | Plaintext corpora, 13 encoding families, the Naibbe cipher, twin and decoy generators, benchmark builder |
| `src/vcl/solvers/` | Language models, simulated-annealing solvers, delta scorer, the validated portfolio attack (`verbose.py`) |
| `src/vcl/models/` | Voynich-native structure models (n-gram, Transformer) |
| `src/vcl/eval/` | Blind evaluator, gates, ledger |
| `src/vcl/agents/`, `src/vcl/neural/` | LLM hypothesis agent (E004) and neural decipherer (E009); both negative results |
| `experiments/` | One numbered script per experiment, plus `LEDGER.csv`, `FAILURES.md`, `results/`, `dev/` probes |
| `reports/` | One report per experiment, pre-registrations (`E0xx_PREREG.md`), methodology, summary |
| `examples/` | Runnable demos |
| `data/` | Transliteration (third-party, see below), derived tables, benchmark |

## Cite us
If you use this code, its methods, data or results, please cite it. GitHub's **"Cite this repository"** button
reads [`CITATION.cff`](CITATION.cff).
```bibtex
@software{jain_2026_voynich_ai_cryptolinguist,
  author    = {Jain, Arham Partap and {Savir Platforms Private Limited}},
  title     = {Voynich AI Cryptolinguist: a pre-registered, known-answer-validated programme
               for deciphering the Voynich Manuscript},
  year      = {2026},
  version   = {0.2.0},
  url       = {https://github.com/Savirinc/voynich-ai-cryptolinguist},
  license   = {MIT}
}
```
Please also cite the sources whose data you use: Zandbergen's ZL transliteration, and Greshko (2025) for the Naibbe
cipher.

## Licence
Code, documentation and results: **MIT**, © 2026 Arham Partap Jain and Savir Platforms Private Limited
([`LICENSE`](LICENSE)). Third-party data and code keep their own terms ([`THIRD_PARTY.md`](THIRD_PARTY.md)).

## Acknowledgements
- René Zandbergen (ZL3b transliteration).
- Michael Greshko (Naibbe cipher, MIT).
- The CLTK Latin Library, Project Gutenberg, and the Beinecke Library (public-domain images).
- Everyone whose published Voynich work this builds on and tests: Currier, Stolfi, Rugg, Timm & Schinner,
  Montemurro & Zanette, Lindemann & Bowern, Davis, Zattera and others.

The research was carried out with Claude (Anthropic) as an AI research assistant, under the project owner's
direction.
