"""Re-run an original ChatGPT-era experiment script unmodified except for its data root.

The scripts hard-code HOME=/mnt/data. We copy the inputs they need into a scratch
directory, substitute only that path, run, and diff the regenerated results.json
against the archived one. Usage:
    python tools/rerun_legacy.py 064
"""
import json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "data/raw/handoff/source_dump"
JOBS = {
    "064": dict(zip="Voynich_Experiment_064_Hypothesis_Tournament.zip", script="run_tournament.py",
                result="voynich_tournament_064/results.json", outdir="voynich_tournament_064"),
    "066": dict(zip="Voynich_Experiment_066_Context_and_Zodiac.zip", script="voynich_experiment_066.py",
                result="voynich_066/results.json", outdir="voynich_066"),
}


def flatten(d, prefix=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from flatten(v, f"{prefix}{k}.")
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from flatten(v, f"{prefix}{i}.")
    else:
        yield prefix[:-1], d


def main(exp):
    job = JOBS[exp]
    work = Path(tempfile.mkdtemp(prefix=f"legacy{exp}_"))
    arch = work / "archive"
    zipfile.ZipFile(DUMP / job["zip"]).extractall(arch)
    for f in ["IVTFF Eva.txt.docx", "voynich_zodiac_slot_map.csv", "voynich_zodiac_clock_positions.csv"]:
        shutil.copy(DUMP / f, work / f)
    shutil.copy(arch / "voynich_tournament_064/indexed_clean_corpus.csv" if (arch / "voynich_tournament_064").exists()
                else next(arch.rglob("indexed_clean_corpus.csv")), work / "indexed_clean_corpus.csv")
    (work / "voynich_tournament_064").mkdir(exist_ok=True)
    shutil.copy(work / "indexed_clean_corpus.csv", work / "voynich_tournament_064/indexed_clean_corpus.csv")
    src = next(arch.rglob(job["script"])).read_text()
    patched = src.replace("Path('/mnt/data')", f"Path({str(work)!r})").replace("'/mnt/data", f"'{work}")
    n_sub = len(re.findall(r"/mnt/data", src))
    script = work / job["script"]
    script.write_text(patched)
    r = subprocess.run([sys.executable, str(script)], cwd=work, capture_output=True, text=True)
    print(f"[legacy {exp}] path substitutions={n_sub} exit={r.returncode}")
    if r.returncode:
        print(r.stderr[-3000:]); sys.exit(1)
    old = dict(flatten(json.loads(next(arch.rglob(Path(job["result"]).name)).read_text())))
    new = dict(flatten(json.loads((work / job["result"]).read_text())))
    diffs = [(k, old.get(k), new.get(k)) for k in sorted(set(old) | set(new))
             if not (isinstance(old.get(k), float) and isinstance(new.get(k), float)
                     and abs(old[k] - new[k]) < 1e-6) and old.get(k) != new.get(k)]
    print(f"[legacy {exp}] archived fields={len(old)} regenerated fields={len(new)} differing={len(diffs)}")
    for k, a, b in diffs[:40]:
        print(f"   {k}: archived={a} rerun={b}")
    out = ROOT / f"experiments/repro/legacy_{exp}_rerun.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"experiment": exp, "workdir": str(work), "fields": len(old),
                               "differing": [{"key": k, "archived": a, "rerun": b} for k, a, b in diffs]},
                              indent=1, default=str))
    print(f"[legacy {exp}] wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1])
