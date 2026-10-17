"""E011c: the FAITHFUL Naibbe cipher (Greshko 2025, author's published tables) scored against Voynich's DEV
fingerprint with exactly the E011 machinery (same DEV blocks, features, noise floor, plaintext chunks, wrapping).

E011 used a Naibbe-STYLE approximation because the tables were believed to be paywalled; they are published under a
modified MIT licence (github greshko/naibbe-cipher @ f2675ec, vendored in external/naibbe/). The cipher has no free
parameters, so there is no search: 20 samples on tune text and 20 on ref text per language, as in E011's final eval.

Run: caffeinate -ims .venv/bin/python experiments/e011c_naibbe_exact.py [--workers 3]
"""
import argparse, json, random, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402  (importable by name so spawned workers can unpickle its functions)
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 11013
LANGS = ["la", "it", "es", "fr", "de", "enm", "cs"]   # he excluded: the cipher has a Latin alphabet only
OUT = ROOT / "experiments/results/e011c.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--n", type=int, default=20)
    a = ap.parse_args()
    t0 = time.time()
    import hashlib
    assert hashlib.sha256(NX.TABLES_CSV.read_bytes()).hexdigest() == NX.TABLES_SHA256
    lines, cur, dev_words, locked = E.voynich_lines()
    pools = T.chunk_pools(dev_words)
    lens = [sum(len(w) for w in l if w) + len([w for w in l if w]) - 1 for l in lines if any(l)]
    width = (float(np.mean(lens)), float(np.std(lens)))
    VF = [E.fingerprint(b) for b, _ in E.cut_blocks(lines, tags=cur)]
    keys = E.FIT + E.HELD
    M = np.array([[f[k] for k in keys] for f in VF])
    mu = dict(zip(keys, M.mean(0)))
    sd = dict(zip(keys, np.maximum(M.std(0, ddof=1), 0.02 * np.abs(M.mean(0)) + 1e-3)))
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = [b | {"role": roles.get(b["id"], {}).get("role")} for b in load_books() if b["lang"] in LANGS]
    chunks = {(lg, r): E.plain_chunks(books, lg, r) for lg in LANGS for r in ("tune", "ref")}
    state = {"pools": pools, "width": width, "mu": mu, "sd": sd, "chunks": chunks}
    rng = random.Random(SEED)
    tasks = [("naibbe_exact", lg, {}, a.n, rng.randrange(2 ** 31)) for lg in LANGS]
    with Pool(a.workers, initializer=E._init, initargs=(state,)) as pool:
        finals = {lg: out for _, lg, out in pool.imap_unordered(E.final_eval, tasks)}
    E._init(state)
    held_nh = [k for k in E.HELD if k != "type_hapax"]
    prev = json.loads((ROOT / "experiments/results/e011.json").read_text())
    res = {"experiment": "e011c", "seed": SEED, "command": " ".join(sys.argv), "tables_sha256": NX.TABLES_SHA256,
           "upstream": "github.com/greshko/naibbe-cipher@f2675ec5dd275268bc64dd48ea64fc0e0e9827a2",
           "citation": "Greshko 2025, Cryptologia, doi:10.1080/01611194.2025.2566408", "langs": {}}
    for lg, out in finals.items():
        r = {}
        for role, fps in out.items():
            if not fps:
                continue
            mf = {k: float(np.mean([f[k] for f in fps])) for k in keys}
            r[role] = {"n": len(fps),
                       "fit": float(np.mean([E.dist(f, E.FIT) for f in fps])),
                       "fit_sd": float(np.std([E.dist(f, E.FIT) for f in fps])),
                       "held": float(np.mean([E.dist(f, E.HELD) for f in fps])),
                       "held_no_hapax": float(np.mean([E.dist(f, held_nh) for f in fps])),
                       "z": {k: round((mf[k] - mu[k]) / sd[k], 2) for k in keys},
                       "mean": {k: round(mf[k], 4) for k in keys}}
        res["langs"][lg] = r
        t = r.get("tune", {})
        print(f"{lg:4s} fit {t.get('fit', float('nan')):.2f} held {t.get('held', float('nan')):.2f} "
              f"held-no-hapax {t.get('held_no_hapax', float('nan')):.2f}  ref fit {r.get('ref', {}).get('fit', float('nan')):.2f}",
              flush=True)
    res["e011_reference"] = {f: {k: prev["best_by_family"][f].get(k) for k in prev["best_by_family"][f]
                                 if not isinstance(prev["best_by_family"][f][k], (dict, list))}
                             for f in prev["best_by_family"]}
    res["voynich_dev"] = {k: round(mu[k], 4) for k in keys}
    res["wall_s"] = round(time.time() - t0)
    OUT.write_text(json.dumps(res, indent=1, default=str))
    from vcl.eval.ledger import append
    append([dict(experiment="E011c", model=f"naibbe_exact/{lg}", checkpoint_sha256=f"tables={NX.TABLES_SHA256[:12]}",
                 split="voynich_DEV_fingerprint", metric=m, value=round(r["tune"][k], 4), command=res["command"],
                 notes="faithful Naibbe (published tables), no search; E011 machinery; tune text")
            for lg, r in res["langs"].items() if "tune" in r
            for m, k in (("fit_rms_z", "fit"), ("heldout_rms_z", "held"), ("heldout_no_hapax_rms_z", "held_no_hapax"))])
    print("wall", res["wall_s"], "s")


if __name__ == "__main__":
    main()
