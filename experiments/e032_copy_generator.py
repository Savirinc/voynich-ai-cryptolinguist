"""E032 (ledger test 3): does the AUTHORS' OWN copy-and-change generator (Timm & Schinner 2019/20, published code,
MIT) reproduce Voynich's measured facts? See reports/E032_PREREG.md. No tuning by us.

Generator: github.com/TorstenTimm/SelfCitationTextgenerator @ a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7,
executable/text-generator.jar (sha256 dc9b2f3c...fef8) with the shipped executable/conf.properties, changing only
text.lines_to_create=3400 (enough for DEV length) and method.random.pseudo.seed = 1..10. Output lines are taken in
order until 28,841 tokens (Voynich DEV size), whole lines only, last line cut.
Features (13): R, NR (E031), wl_mean, types, h2, I_word, top_word (E019), PERS_30, COV_30 (E021), type_hapax,
zipf_slope (E011), NSUF95, DIST (E026 segmenter, same settings).
Run: caffeinate -ims .venv/bin/python experiments/e032_copy_generator.py GENERATOR_DIR JAVA
"""
from __future__ import annotations

import hashlib, json, math, random, re, subprocess, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e019_unit_burstiness import burst  # noqa: E402
from e021_persistence import persistence  # noqa: E402
from e031_copy_pairs import stats as pair_stats  # noqa: E402
from vcl.solvers.segment import ending_features, segment_types  # noqa: E402

SEED = 32032
OUT = ROOT / "experiments/results/e032.json"
FEATS = ["R", "NR", "wl_mean", "types", "h2", "I_word", "top_word", "PERS_30", "COV_30", "type_hapax", "zipf_slope",
         "NSUF95", "DIST"]
SEG = dict(max_suf=4, min_stem=2, a_s=1.0, a_f=1e-6, sweeps=120, t0=3.0, t1=0.05, smooth=0.01)   # = E026
SEEDS, Z_OK = list(range(1, 11)), 3.0
JAR_SHA = "dc9b2f3cd4e930e45f093fc096bdf0aef54bbe760f558858af1cdf09ad18fef8"


def h2(tokens):
    c1, c2 = Counter(), Counter()
    for w in tokens:
        s = "#" + w
        c1.update(s); c2.update(zip(s, s[1:] + "#"))
    H = lambda c: -sum(v / sum(c.values()) * math.log2(v / sum(c.values())) for v in c.values())
    return H(c2) - H(c1)


def features(lines, seed):
    toks = [w for l in lines for w in l]
    ps = pair_stats(lines, random.Random(seed))
    wc = Counter(toks)
    fr = np.array(sorted(wc.values(), reverse=True)[:100], float)
    Iw, Tw, _ = burst(toks)
    pe = persistence(toks)
    ef = ending_features(toks, segment_types(Counter(toks), seed=seed, **SEG))
    return {"R": ps["R"], "NR": ps["NR"], "wl_mean": float(np.mean([len(w) for w in toks])), "types": float(len(wc)),
            "h2": h2(toks), "I_word": Iw, "top_word": Tw, "PERS_30": pe["PERS_30"], "COV_30": pe["COV_30"],
            "type_hapax": sum(v == 1 for v in wc.values()) / len(wc),
            "zipf_slope": float(np.polyfit(np.log(np.arange(1, len(fr) + 1)), np.log(fr), 1)[0]),
            "NSUF95": ef["NSUF95"], "DIST": ef["DIST"]}


def generate(gen_dir: Path, java: str, seed: int, n: int, work: Path):
    d = work / f"seed{seed}"; (d / "generate").mkdir(parents=True, exist_ok=True)
    conf = (gen_dir / "executable/conf.properties").read_text()
    conf = re.sub(r"(?m)^text\.lines_to_create=.*$", "text.lines_to_create=3400", conf)
    conf = re.sub(r"(?m)^method\.random\.pseudo\.seed=.*$", f"method.random.pseudo.seed={seed}", conf)
    (d / "conf.properties").write_text(conf)
    subprocess.run([java, "-jar", str(gen_dir / "executable/text-generator.jar")], cwd=d, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lines, k = [], 0
    for ln in (d / "generate/generated_text.txt").read_text().splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        ws = ln.split()
        if k + len(ws) >= n:
            lines.append(ws[:n - k]); break
        lines.append(ws); k += len(ws)
    assert sum(map(len, lines)) == n, "generator output too short"
    return lines


def run(task):
    gen_dir, java, seed, n, work = task
    return features(generate(Path(gen_dir), java, seed, n, Path(work)), SEED + seed)


def main():
    gen_dir, java = Path(sys.argv[1]), sys.argv[2]
    assert hashlib.sha256((gen_dir / "executable/text-generator.jar").read_bytes()).hexdigest() == JAR_SHA
    lines, _, dev_words, locked = E.voynich_lines()
    vl = [[w for w in l if w] for l in lines if any(l)]
    n = len(dev_words)
    work = ROOT / "experiments/results/e032_work"
    with Pool(3) as pool:
        G = pool.map(run, [(str(gen_dir), java, s, n, str(work)) for s in SEEDS])
    V = features(vl, SEED)
    M = {k: float(np.mean([g[k] for g in G])) for k in FEATS}
    S = {k: max(float(np.std([g[k] for g in G], ddof=1)), 0.02 * abs(V[k]), 0.01) for k in FEATS}
    Z = {k: round((V[k] - M[k]) / S[k], 2) for k in FEATS}
    fail = [k for k in FEATS if abs(Z[k]) > Z_OK]
    if len(fail) <= 1:
        verdict, bf = "M REPRODUCES", {"M": 10.0}
    elif len(fail) <= 4:
        verdict, bf = "PARTIAL", {}
    else:
        verdict, bf = "AUTHORS' GENERATOR FAILS", {"M": 1 / 3}
    out = {"experiment": "E032", "generator": "TorstenTimm/SelfCitationTextgenerator@a6ede22", "jar_sha256": JAR_SHA,
           "seeds": SEEDS, "n_tokens": n, "voynich": V, "gen_mean": M, "gen_sd": S, "z": Z, "fail": fail,
           "gen_samples": G, "verdict": verdict, "bayes_factors": bf, "locked_test_excluded": locked}
    OUT.write_text(json.dumps(out, indent=1))
    for k in FEATS:
        print(f"{k:11s} V {V[k]:9.4f}  gen {M[k]:9.4f} ± {S[k]:.4f}  z {Z[k]:+.2f}{'  FAIL' if k in fail else ''}")
    print(verdict, bf, "fails:", fail)


if __name__ == "__main__":
    main()
