"""E014: repetition mechanisms (nulls, ditto, spelling memory) on top of the E013 edge-aware twins -- can they close
the held-out gap (adjacent repeats, one-glyph words, hapax share) while the remaining independent features stay in
range, and which are necessary?

Pre-registered in reports/E014_PREREG.md (read-only; sha256 stored in the output). Same machinery as E013; the three
E013 misses (adj_repeat, wl_1, type_hapax) move into FIT; HELD = the six remaining independent features. Families
(src/vcl/synthetic/rep_twins.py): naibbe_rep x {la, it, fr, de}; rugg_rep; self_citation_rep.

Run: caffeinate -ims .venv/bin/python experiments/e014_rep_twins.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, random, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 14014
PREREG = ROOT / "reports/E014_PREREG.md"
OUT = ROOT / "experiments/results/e014.json"
LANGS = ["la", "it", "fr", "de"]
LANG_FAMS = ["naibbe_rep"]
DECOY_FAMS = ["rugg_rep", "self_citation_rep"]
MOVED = ["edge_excess", "yq_logor", "mfinal_logor", "adj_repeat", "wl_1", "type_hapax"]
FIT = E.FIT + MOVED
HELD = [k for k in E.HELD if k not in MOVED]
N_SHUF = 5
MECH = {"nulls": dict(p_null=0.0), "ditto": dict(p_rep=0.0), "memory": dict(p_reuse=0.0), "sandhi": dict(beta=0.0, k=1)}


def _mi(pairs):
    n = len(pairs)
    if n == 0:
        return 0.0
    j = Counter(pairs); a = Counter(x for x, _ in pairs); b = Counter(y for _, y in pairs)
    return float(sum(v / n * np.log2(v * n / (a[x] * b[y])) for (x, y), v in j.items()))


def edge_excess(lines, rng):
    def pairs(ls):
        return [(x[-1], y[0]) for l in ls for x, y in zip(l, l[1:]) if x and y]
    obs = _mi(pairs(lines))
    sh = []
    for _ in range(N_SHUF):
        ls = []
        for l in lines:
            l = list(l); rng.shuffle(l); ls.append(l)
        sh.append(_mi(pairs(ls)))
    return obs - float(np.mean(sh))


def fingerprint(lines, seed=0):
    f = E.fingerprint(lines)
    f["edge_excess"] = edge_excess(lines, random.Random(seed))
    return f


G = {}


def _init(state):
    G.update(state)
    E._init(state)


def sample_fp(family, params, seed, chunk=None):
    n_words = int(E.BLOCK / 5.0 * 1.4)
    g = R.generate(family, params, seed, G["pools"], n_words, G["C"], G["nulls"], plain=chunk, width_mean=G["width"][0],
                   width_sd=G["width"][1])
    blocks = E.cut_blocks(g["lines"])
    return fingerprint(blocks[0][0], seed) if blocks else None


def dist(f, keys):
    if f is None:
        return 1e9
    return float(np.sqrt(np.mean([((f[k] - G["mu"][k]) / G["sd"][k]) ** 2 for k in keys])))


def search_combo(task):
    family, lang, n_rand, n_ref, seed = task
    rng = random.Random(seed)
    chunks = G["chunks"].get((lang, "tune"), [None]) if lang else [None]
    t0, best, trace = time.time(), (1e9, None, None), []
    for i in range(n_rand + n_ref):
        p = (R.random_params(family, rng) if i < n_rand or best[1] is None else
             R.perturb_params(family, best[1], rng, scale=0.15 if i < n_rand + n_ref // 2 else 0.07))
        ch = rng.choice(chunks); s = rng.randrange(2 ** 31)
        try:
            f = sample_fp(family, p, s, ch[2] if ch else None)
        except Exception:  # noqa: BLE001
            f = None
        d = dist(f, FIT); trace.append(d)
        if d < best[0]:
            best = (d, p, s)
    return {"family": family, "lang": lang, "best_search_distance": best[0], "params": best[1],
            "n_evals": len(trace), "median_trial": float(np.median(trace)), "wall_s": round(time.time() - t0, 1)}


def final_eval(task):
    tag, family, lang, params, n, seed = task
    rng = random.Random(seed)
    out = {}
    for role in (["tune", "ref"] if lang else ["none"]):
        chunks = G["chunks"].get((lang, role), []) if lang else [None]
        fps = []
        for _ in range(n):
            ch = rng.choice(chunks) if chunks else None
            f = sample_fp(family, params, rng.randrange(2 ** 31), ch[2] if ch else None)
            if f is not None:
                fps.append(f)
        out[role] = fps
    return tag, out


def summarise(fps, keys):
    mf = {k: float(np.mean([f[k] for f in fps])) for k in keys}
    return {"n": len(fps),
            "fit": float(np.mean([dist(f, FIT) for f in fps])), "fit_sd": float(np.std([dist(f, FIT) for f in fps])),
            "held": float(np.mean([dist(f, HELD) for f in fps])),
            "held_no_hapax": float(np.mean([dist(f, [k for k in HELD if k != "type_hapax"]) for f in fps])),
            "held_distances": [round(dist(f, HELD), 4) for f in fps],
            "z": {k: round((mf[k] - G["mu"][k]) / G["sd"][k], 2) for k in keys},
            "mean": {k: round(mf[k], 4) for k in keys}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    n_rand, n_ref, n_final = (140, 160, 20) if not a.smoke else (3, 3, 2)
    langs = LANGS if not a.smoke else ["la"]

    lines, cur, dev_words, locked = E.voynich_lines()
    pools = T.chunk_pools(dev_words)
    C = X.coupling_matrix(lines)
    lens = [sum(len(w) for w in l if w) + len([w for w in l if w]) - 1 for l in lines if any(l)]
    width = (float(np.mean(lens)), float(np.std(lens)))
    VF = [fingerprint(b, i) for i, (b, _) in enumerate(E.cut_blocks(lines, tags=cur))]
    keys = FIT + HELD
    M = np.array([[f[k] for k in keys] for f in VF])
    mu = dict(zip(keys, M.mean(0)))
    sd = dict(zip(keys, np.maximum(M.std(0, ddof=1), 0.02 * np.abs(M.mean(0)) + 1e-3)))
    loo = {}
    for name, ks in (("fit", FIT), ("held", HELD)):
        ds = []
        for i in range(len(VF)):
            m_i = {k: np.mean([VF[j][k] for j in range(len(VF)) if j != i]) for k in ks}
            ds.append(float(np.sqrt(np.mean([((VF[i][k] - m_i[k]) / sd[k]) ** 2 for k in ks]))))
        loo[name] = {"median": float(np.median(ds)), "p90": float(np.percentile(ds, 90))}
    print(f"DEV blocks {len(VF)}; edge_excess mean {mu['edge_excess']:.3f} sd {sd['edge_excess']:.3f}; floors {loo}",
          flush=True)
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = [b | {"role": roles.get(b["id"], {}).get("role")} for b in load_books() if b["lang"] in langs]
    chunks = {(lg, r): E.plain_chunks(books, lg, r) for lg in langs for r in ("tune", "ref")}
    state = {"pools": pools, "width": width, "mu": mu, "sd": sd, "chunks": chunks, "C": C,
             "nulls": R.null_pool(dev_words)}
    rng = random.Random(SEED)
    tasks = [(f, lg, n_rand, n_ref, rng.randrange(2 ** 31)) for f in LANG_FAMS for lg in langs]
    tasks += [(f, None, 3 * n_rand, 3 * n_ref, rng.randrange(2 ** 31)) for f in DECOY_FAMS]
    tasks.sort(key=lambda t: -(t[2] + t[3]))
    with Pool(a.workers, initializer=_init, initargs=(state,)) as pool:
        searched = []
        for r in pool.imap_unordered(search_combo, tasks):
            searched.append(r)
            print(f"  search {r['family']:18s} {str(r['lang']):4s} best {r['best_search_distance']:.3f} "
                  f"median {r['median_trial']:.2f} ({r['n_evals']} evals, {r['wall_s']} s)", flush=True)
        t_search = time.time() - t0
        # final eval: full spec, the three ablations (one mechanism switched off), all mechanisms off
        ft = []
        for r in searched:
            base = (r["family"], r["lang"])
            ft.append(((*base, "full"), r["family"], r["lang"], r["params"], n_final, rng.randrange(2 ** 31)))
            for m, off in MECH.items():
                if any(k_ not in r["params"] for k_ in off):
                    continue
                ft.append(((*base, f"no_{m}"), r["family"], r["lang"], {**r["params"], **off}, n_final,
                           rng.randrange(2 ** 31)))
            ft.append(((*base, "none"), r["family"], r["lang"], {**r["params"], **{k_: v for k_, v in {**X.EDGE_OFF, **R.REP_OFF}.items() if k_ in r["params"]}}, n_final,
                       rng.randrange(2 ** 31)))
        finals = dict(pool.imap_unordered(final_eval, ft))
    _init(state)

    res = {"experiment": "e014", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha, "seed": SEED,
           "command": " ".join(sys.argv), "fit_features": FIT, "held_features": HELD, "noise_floor": loo,
           "voynich_dev_mean": {k: round(mu[k], 4) for k in keys}, "combos": []}
    for r in searched:
        c = {k: r[k] for k in ("family", "lang", "params", "best_search_distance", "median_trial", "n_evals")}
        c["is_language"] = R.IS_LANGUAGE[r["family"]]
        for v in ["full", "none"] + [f"no_{m}" for m in MECH if (r["family"], r["lang"], f"no_{m}") in finals]:
            out = finals[(r["family"], r["lang"], v)]
            c[v] = {role: summarise(fps, keys) for role, fps in out.items() if fps}
        main_role = "tune" if r["lang"] else "none"
        full = c["full"][main_role]["fit"]
        c["mechanism_effect_fit"] = {m: round(c[f"no_{m}"][main_role]["fit"] - full, 3) for m in MECH if f"no_{m}" in c}
        c["necessary_mechanisms"] = [m for m, d in c["mechanism_effect_fit"].items() if d > 0.25]
        c["twin"] = bool(full <= loo["fit"]["p90"])
        res["combos"].append(c)
        print(f"{r['family']:18s} {str(r['lang']):4s} fit {full:.2f} (none {c['none'][main_role]['fit']:.2f}) "
              f"held {c['full'][main_role]['held']:.2f} edge z {c['full'][main_role]['z']['edge_excess']} adj z {c['full'][main_role]['z']['adj_repeat']} "
              f"effects {c['mechanism_effect_fit']}", flush=True)

    from scipy.stats import mannwhitneyu
    role = lambda c: "tune" if c["lang"] else "none"
    mean_c = [c for c in res["combos"] if c["is_language"]]
    dec_c = [c for c in res["combos"] if not c["is_language"]]
    bm = min(mean_c, key=lambda c: c["full"][role(c)]["fit"])
    bd = min(dec_c, key=lambda c: c["full"][role(c)]["fit"])
    mw = mannwhitneyu(bm["full"]["tune"]["held_distances"], bd["full"]["none"]["held_distances"],
                      alternative="two-sided")
    twins = [f"{c['family']}/{c['lang']}" for c in res["combos"] if c["twin"]]
    hm, hd = bm["full"]["tune"]["held"], bd["full"]["none"]["held"]
    ident = ("MEANINGFUL FAVOURED" if mw.pvalue < 0.01 and hm < hd else
             "MEANINGLESS FAVOURED" if mw.pvalue < 0.01 and hd < hm else "NOT IDENTIFIABLE")
    res["identifiability"] = {"best_meaningful": f"{bm['family']}/{bm['lang']}", "best_meaningless": bd["family"],
                              "held_meaningful": hm, "held_meaningless": hd, "mannwhitney_p": float(mw.pvalue),
                              "verdict": ident}
    res["verdict"] = (f"TWINS: {twins}" if twins else
                      f"NO TWIN (best fit {min(c['full'][role(c)]['fit'] for c in res['combos']):.2f} vs floor p90 "
                      f"{loo['fit']['p90']:.2f})") + f"; identifiability: {ident}"
    res["wall_s"] = {"search": round(t_search), "total": round(time.time() - t0)}
    out_path = OUT if not a.smoke else ROOT / "experiments/results/smoke/e014_smoke.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=1, default=str))
    print(res["verdict"]); print(json.dumps(res["identifiability"], indent=1))
    if not a.smoke:
        from vcl.eval.ledger import append
        append([dict(experiment="E014", model=f"{c['family']}/{c['lang']}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                     split="voynich_DEV_fingerprint", metric=m, value=round(v, 4), command=res["command"],
                     notes=f"pre-registered; {res['verdict'][:120]}")
                for c in res["combos"]
                for m, v in (("fit_rms_z", c["full"][role(c)]["fit"]), ("heldout_rms_z", c["full"][role(c)]["held"]),
                             ("edge_excess_z", c["full"][role(c)]["z"]["edge_excess"]))])


if __name__ == "__main__":
    main()
