# VCL patches to NeuroDecipher

Upstream: https://github.com/j-luo93/NeuroDecipher @ `480bad2487820e3737fecfdd108214efa769e34b`
(2021-09-20, "updated README.md"); submodules `arglib` @ `91b41f5b71f035ee931ef3692d8f72a9e8520757`,
`dev_misc` @ `6c711b48ab11c90fd25655895810e82d560037b0`. Shallow clone + `git submodule update --init`.

**Licence:** upstream code (main repo, arglib, dev_misc) has NO licence (no LICENSE file, GitHub `license: null`),
so all rights are reserved by the author. We therefore do not redistribute it: everything under
`external/neurodecipher/` is gitignored except this file and `vcl_patches.diff`. The vendored `editdistance/`
is MIT (Hiroyuki Tanaka). The data files (no licence stated) were moved to the gitignored
`external/neurodecipher_data_private/`; see `reports/EXTERNAL_BASELINES.md`.

## Rebuilding the environment

```
git clone --depth 1 https://github.com/j-luo93/NeuroDecipher external/neurodecipher
cd external/neurodecipher && git checkout 480bad2 && git submodule update --init
git apply vcl_patches.diff          # main-repo hunks; dev_misc hunk: (cd dev_misc && git apply -p2 ...) or edit by hand
mkdir -p ../neurodecipher_data_private && mv data/* ../neurodecipher_data_private/
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python "torch==2.5.1" "numpy<2" pandas prettytable treelib enlighten \
    pytrie colorlog cachetools "cython<3" ortools tensorboard setuptools
uv pip install --python .venv/bin/python --no-build-isolation ./editdistance
uv pip install --python .venv/bin/python --no-build-isolation -e ./arglib -e ./dev_misc -e .
```
Resolved versions: Python 3.10.20, torch 2.5.1 (CPU, macOS arm64), numpy 1.26.4, ortools 9.14.6206, pandas 2.3.3
(full freeze: `external/neurodecipher_runs/pip_freeze.txt`). tensorflow and cvxopt from upstream
`requirements.txt` are NOT installed (see patches 2 and 4).

Linear B data prep (no code change): upstream `.cog` headers are `linear_b`/`greek`, but the charsets are
registered as `minoan`/`el`, so we write header-relabelled copies `linear_b-greek{,.names}.minoan-el.cog`
(body byte-identical). Without this, `get_charset('greek')` raises `KeyError`.

## Patches (all marked `VCL_PATCH` in source; full diff in `vcl_patches.diff`)

| # | File | Problem | Fix | Effect on algorithm |
|---|------|---------|-----|---------------------|
| 1 | `editdistance/setup.py` | `-fopenmp` and `-L/usr/lib/x86_64-linux-gnu/` fail with Apple clang | drop both flags | none; Cython `prange` runs serially |
| 2 | `nd/flow/min_cost_flow.py` | `ortools.graph.pywrapgraph` removed in ortools >= 9.4; `cvxopt` imported but unused | use `ortools.graph.python.min_cost_flow.SimpleMinCostFlow` (snake_case methods); drop cvxopt import | none (same solver, same graph) |
| 3 | `nd/dataset/data_loader.py::_get_item` | numpy >= 1.24 raises on ragged `np.asarray` | fall back to an explicit 1-D object array (what numpy < 1.24 produced) | none |
| 4 | `dev_misc/dev_misc/__init__.py` | eager `import tensorflow` via `tb2df` (unused by `nd`) | wrap in `try/except ImportError` | none |

Also note: README says `--cfg`, but arglib's flag is `--config` (or `-cfg`).

## Run hygiene

Upstream code was read before running (no network/subprocess/eval/pickle-from-untrusted calls; writes only to
`./log/<date>/<cfg>/` under cwd). It is run only as `.venv/bin/python -I -m nd.main ...` with cwd set to a fresh
directory under `external/neurodecipher_runs/`, with a minimal environment and OMP_NUM_THREADS=2, from
`experiments/e008_neurodecipher_baseline.py`.
