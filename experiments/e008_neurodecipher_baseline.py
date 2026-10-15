"""E008: NeuroDecipher (Luo, Cao & Barzilay, ACL 2019) as an external positive-control baseline.

Real-script, KNOWN-RELATIVE regime: Ugaritic->Hebrew and Linear B->Greek cognate identification.
This is NOT our ciphertext-only benchmark; see reports/EXTERNAL_BASELINES.md. No Voynich data is touched.

Upstream code and data have no licence, so neither is redistributed: the code lives (gitignored) in
external/neurodecipher/ with its own isolated venv; data in external/neurodecipher_data_private/ (gitignored).
Compatibility patches: external/neurodecipher_patches/VCL_PATCHES.md + vcl_patches.diff.

Untrusted-code hygiene: upstream code is run only via its own interpreter with `python -I -m nd.main`,
cwd = a fresh run dir under external/neurodecipher_runs/ (also gitignored), never imported into this process.

Usage:
  .venv/bin/python experiments/e008_neurodecipher_baseline.py run --runs uga_small        # one run
  .venv/bin/python experiments/e008_neurodecipher_baseline.py run --runs uga_small,linb   # several, sequential
  .venv/bin/python experiments/e008_neurodecipher_baseline.py collect [--ledger]         # parse logs -> e008.json
"""
import argparse, hashlib, json, os, platform, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ND = ROOT / "external/neurodecipher"
ND_PY = ND / ".venv/bin/python"
DATA = ROOT / "external/neurodecipher_data_private"
RUNS = ROOT / "external/neurodecipher_runs"
OUT = ROOT / "experiments/results/e008.json"
THREADS = "2"  # keep CPU modest; another experiment shares the machine

# Paper numbers (arXiv:1906.06718 v1, Tables 2-3), cognate identification accuracy (%).
PAPER = {
    "uga_noisy": {"NeuroCipher": 65.9, "Bayesian (Snyder+2010)": 60.4},
    "uga_noiseless": {"NeuroCipher": 93.5, "Matcher (Berg-Kirkpatrick&Klein 2011)": 90.4},
    "linb": {"NeuroCipher": 84.7},
    "linb_names": {"NeuroCipher": 67.3},
}

# Every run uses --config UgaHebSmallNoSpe (the only config shipped upstream; arglib requires one) and
# overrides fields on the CLI. uga_small == the released config verbatim (noisy Ugaritic, 10% subset).
RUN_SPECS = {
    "uga_small": dict(
        paper_key="uga_noisy",
        note="released upstream config UgaHebSmallNoSpe verbatim (10% noisy subset: 221 cognate pairs, "
             "514 unpaired Ugaritic, 3800 unpaired Hebrew); upstream evaluates on the cognate-bearing "
             "Ugaritic words of the SAME 10% file, whereas the paper reports testing on the full dataset.",
        args=["--cog_path", str(DATA / "uga-heb.small.no_spe.cog")],
    ),
    "linb": dict(
        paper_key="linb",
        note="NO upstream Linear B config; reconstructed from paper sec.5 (universal charset 100, flow "
             "decay gamma=0.9, capacity 1, all 919 pairs targeted from round 1). Paper's Linear-B-specific "
             "regulariser Omega_2 and random restarts are NOT in the released code -> single restart, "
             "Ugaritic regulariser. Epochs/rounds not given in paper: we use 5 rounds x 60 epochs.",
        args=["--cog_path", str(DATA / "linear_b-greek.minoan-el.cog"), "--lost_lang", "minoan", "--known_lang", "el",
              "--universal_charset_size", "100", "--momentum", "0.9", "--capacity", "1",
              "--num_cognates", "919", "--inc", "919", "--num_rounds", "5", "--num_epochs_per_M_step", "60",
              "--warm_up_steps", "1"],
    ),
    "linb_names": dict(
        paper_key="linb_names",
        note="as linb but Greek side restricted to names (455 pairs, 464 unpaired Linear B words); cognate "
             "target grows by 50/round (paper: 'gradually increase'); 11 rounds x 60 epochs.",
        args=["--cog_path", str(DATA / "linear_b-greek.names.minoan-el.cog"), "--lost_lang", "minoan",
              "--known_lang", "el", "--universal_charset_size", "100", "--momentum", "0.9",
              "--capacity", "1", "--num_cognates", "455", "--inc", "50", "--num_rounds", "11",
              "--num_epochs_per_M_step", "60", "--warm_up_steps", "1"],
    ),
}


def cmd_for(name):
    return [str(ND_PY), "-I", "-m", "nd.main", "--config", "UgaHebSmallNoSpe", *RUN_SPECS[name]["args"]]


def run(names):
    env = {"PATH": "/usr/bin:/bin", "OMP_NUM_THREADS": THREADS, "MKL_NUM_THREADS": THREADS, "HOME": os.environ["HOME"]}
    for name in names:
        d = RUNS / name
        d.mkdir(parents=True, exist_ok=True)
        cmd = cmd_for(name)
        (d / "command.txt").write_text(" ".join(cmd) + "\n")
        t0 = time.time()
        with open(d / "stdout.log", "w") as f:
            rc = subprocess.call(cmd, cwd=d, env=env, stdout=f, stderr=subprocess.STDOUT)
        (d / "status.json").write_text(json.dumps({"returncode": rc, "seconds": round(time.time() - t0, 1)}))
        print(name, "rc", rc, f"{time.time() - t0:.0f}s", flush=True)


ROW = re.compile(r"\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(mle|flow)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\d+)/(\d+)=")
EPOCH = re.compile(r"Epoch: (\d+)")


def parse_log(path):
    """Return {epoch: {setting: (correct, total)}} from upstream PrettyTable eval output."""
    evals, ep = {}, None
    for line in path.read_text(errors="replace").splitlines():
        m = EPOCH.search(line)
        if m:
            ep = int(m.group(1)); evals.setdefault(ep, {})
            continue
        m = ROW.search(line)
        if m and ep is not None:
            mode, edit, cap = m.group(3), m.group(4), m.group(5)
            key = "mle" if mode == "mle" else f"flow_edit{edit}_cap{cap}"
            evals[ep][key] = (int(m.group(6)), int(m.group(7)))
    return evals


def env_versions():
    code = ("import torch,numpy,ortools,pandas,sys,platform;print(sys.version.split()[0],torch.__version__,"
            "numpy.__version__,ortools.__version__,pandas.__version__,platform.machine())")
    out = subprocess.run([str(ND_PY), "-I", "-c", code], capture_output=True, text=True, cwd="/").stdout.split()
    return dict(zip(["python", "torch", "numpy", "ortools", "pandas", "machine"], out))


def git_rev(path):
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def collect(write_ledger):
    res = {
        "experiment": "e008",
        "description": "NeuroDecipher external baseline: real-script positive control (lost script + KNOWN relative)",
        "upstream": {"repo": "https://github.com/j-luo93/NeuroDecipher", "commit": git_rev(ND),
                     "submodules": {"arglib": git_rev(ND / "arglib"), "dev_misc": git_rev(ND / "dev_misc")},
                     "paper": "Luo, Cao, Barzilay. ACL 2019. arXiv:1906.06718",
                     "licence_code": "NONE (no LICENSE file; GitHub license=null) -> not redistributed",
                     "licence_data": "NONE stated; Ugaritic-Hebrew from Snyder et al. 2010 (obtained privately by "
                                     "authors); Linear B extracted from a Linear B lexicon scan on archive.org -> "
                                     "kept in gitignored external/neurodecipher_data_private/"},
        "data_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(DATA.iterdir()) if f.is_file()},
        "env": env_versions(), "threads": int(THREADS), "patches": "external/neurodecipher_patches/VCL_PATCHES.md",
        "paper_numbers_pct": PAPER, "runs": {},
    }
    rows = []
    for name, spec in RUN_SPECS.items():
        d = RUNS / name
        if not (d / "stdout.log").exists():
            res["runs"][name] = {"status": "not_run"}
            continue
        evals = parse_log(d / "stdout.log")
        status = json.loads((d / "status.json").read_text()) if (d / "status.json").exists() else {"returncode": None}
        if not evals:
            res["runs"][name] = {"status": "no_evals", **status}
            continue
        last = max(evals)
        final = {k: round(100 * c / t, 2) for k, (c, t) in evals[last].items()}
        n_eval = next(iter(evals[last].values()))[1]
        # Best-over-epochs is selection on the evaluation set itself (upstream has no held-out split) ->
        # reported only as an optimistic upper bound, never as the headline.
        best = {k: round(max(100 * e[k][0] / e[k][1] for e in evals.values() if k in e), 2) for k in evals[last]}
        primary = "flow_editTrue_cap" + ("3" if name.startswith("uga") else "1")
        res["runs"][name] = {
            "status": ("complete" if status.get("returncode") == 0 else
                       "PARTIAL (no status.json: still running or killed)" if status.get("returncode") is None
                       else f"FAILED returncode={status.get('returncode')}"),
            "seconds": status.get("seconds"), "command": (d / "command.txt").read_text().strip(),
            "note": spec["note"], "n_eval_lost_words": n_eval, "final_epoch": last,
            "final_acc_pct": final, "best_over_epochs_acc_pct_OPTIMISTIC": best,
            "primary_metric": primary, "primary_final_pct": final.get(primary),
            "paper_pct": PAPER[spec["paper_key"]]["NeuroCipher"],
            "curve_primary_pct": {ep: round(100 * e[primary][0] / e[primary][1], 2) for ep, e in sorted(evals.items()) if primary in e},
        }
        rows.append(dict(experiment="e008", model=f"NeuroDecipher@{res['upstream']['commit'][:12]}",
                         checkpoint_sha256="", split=f"external:{name}", metric=f"cognate_acc_pct_{primary}_final",
                         value=final.get(primary),
                         command=".venv/bin/python experiments/e008_neurodecipher_baseline.py run --runs " + name,
                         notes=f"paper={PAPER[spec['paper_key']]['NeuroCipher']}; n_eval={n_eval}; epoch={last}; "
                               f"{res['runs'][name]['status']}; see experiments/results/e008.json"))
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v.get("primary_final_pct", v.get("status")) for k, v in res["runs"].items()}, indent=1))
    if write_ledger and rows:
        sys.path.insert(0, str(ROOT / "src"))
        from vcl.eval.ledger import append
        append(rows)
        print(f"appended {len(rows)} ledger rows")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--runs", default="uga_small")
    c = sub.add_parser("collect"); c.add_argument("--ledger", action="store_true")
    a = ap.parse_args()
    if a.cmd == "run":
        run([n for n in a.runs.split(",") if n])
    else:
        collect(a.ledger)


if __name__ == "__main__":
    main()
