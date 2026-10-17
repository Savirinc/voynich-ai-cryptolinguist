"""E015: is "meaningful favoured" real? The E014 cipher model fed MEANINGLESS input with the same letter statistics.

Pre-registered in reports/E015_PREREG.md. Conditions per language (la, it, fr, de), all with the identical
naibbe_rep machinery (E014: published Naibbe tables + sandhi + nulls + ditto + memory + respacing + line-end m),
identical search budget (140 + 160) and final evaluation (20 samples, tune and ref text):
  real      the E011 plaintext chunks as they are
  shufword  the same chunks with word order shuffled (real words, no syntax)
  shufchar  the same chunks with all letters shuffled (same letter frequencies, no words, no syntax)
Machinery and features exactly as E014 (imported from experiments/e014_rep_twins.py).

Run: caffeinate -ims .venv/bin/python experiments/e015_shuffled_controls.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, random, sys, time, zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e014_rep_twins as R14  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 15015
PREREG = ROOT / "reports/E015_PREREG.md"
OUT = ROOT / "experiments/results/e015.json"
LANGS = ["la", "it", "fr", "de"]
CONDS = ["real", "shufword", "shufchar"]
ALPHA = 0.01


def transform(text: str, cond: str, seed: int) -> str:
    rng = random.Random(seed)
    if cond == "real":
        return text
    if cond == "shufword":
        ws = text.split(" "); rng.shuffle(ws); return " ".join(ws)
    letters = [c for c in text if c != " "]
    rng.shuffle(letters)
    it = iter(letters)
    return "".join(c if c == " " else next(it) for c in text)


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
    FIT, HELD = R14.FIT, R14.HELD

    lines, cur, dev_words, _ = E.voynich_lines()
    pools = T.chunk_pools(dev_words)
    C = X.coupling_matrix(lines)
    lens = [sum(len(w) for w in l if w) + len([w for w in l if w]) - 1 for l in lines if any(l)]
    width = (float(np.mean(lens)), float(np.std(lens)))
    VF = [R14.fingerprint(b, i) for i, (b, _) in enumerate(E.cut_blocks(lines, tags=cur))]
    keys = FIT + HELD
    M = np.array([[f[k] for k in keys] for f in VF])
    mu = dict(zip(keys, M.mean(0)))
    sd = dict(zip(keys, np.maximum(M.std(0, ddof=1), 0.02 * np.abs(M.mean(0)) + 1e-3)))
    loo = {}
    for name, ks in (("fit", FIT), ("held", HELD)):
        ds = [float(np.sqrt(np.mean([((VF[i][k] - np.mean([VF[j][k] for j in range(len(VF)) if j != i])) / sd[k]) ** 2
                                     for k in ks]))) for i in range(len(VF))]
        loo[name] = {"median": float(np.median(ds)), "p90": float(np.percentile(ds, 90))}
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = [b | {"role": roles.get(b["id"], {}).get("role")} for b in load_books() if b["lang"] in langs]
    chunks = {}
    for lg in langs:
        for role in ("tune", "ref"):
            base = E.plain_chunks(books, lg, role)
            for cond in CONDS:
                chunks[(f"{lg}:{cond}", role)] = [(bid, off, transform(t, cond, zlib.crc32(f"{bid}|{off}|{cond}".encode())))
                                                  for bid, off, t in base]
    state = {"pools": pools, "width": width, "mu": mu, "sd": sd, "chunks": chunks, "C": C,
             "nulls": R.null_pool(dev_words)}
    rng = random.Random(SEED)
    tasks = [("naibbe_rep", f"{lg}:{c}", n_rand, n_ref, rng.randrange(2 ** 31)) for lg in langs for c in CONDS]
    with Pool(a.workers, initializer=R14._init, initargs=(state,)) as pool:
        searched = []
        for r in pool.imap_unordered(R14.search_combo, tasks):
            searched.append(r)
            print(f"  search {r['lang']:12s} best {r['best_search_distance']:.3f} median {r['median_trial']:.2f}",
                  flush=True)
        ft = [((r["lang"], "full"), r["family"], r["lang"], r["params"], n_final, rng.randrange(2 ** 31))
              for r in searched]
        finals = dict(pool.imap_unordered(R14.final_eval, ft))
    R14._init(state)

    from scipy.stats import mannwhitneyu
    res = {"experiment": "e015", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha, "seed": SEED,
           "command": " ".join(sys.argv), "noise_floor": loo, "conditions": {}, "comparisons": {}}
    per = {}
    for r in searched:
        out = finals[(r["lang"], "full")]
        s = {role: R14.summarise(fps, keys) for role, fps in out.items() if fps}
        s["tune"]["fit_distances"] = [round(R14.dist(f, FIT), 4) for f in out["tune"]]
        per[r["lang"]] = s
        res["conditions"][r["lang"]] = {"params": r["params"], **{role: {k: v[k] for k in ("fit", "held", "z")}
                                                                   for role, v in s.items()},
                                        "twin": bool(s["tune"]["fit"] <= loo["fit"]["p90"]),
                                        "full_twin": bool(s["tune"]["fit"] <= loo["fit"]["p90"]
                                                          and s["tune"]["held"] <= loo["held"]["p90"])}
    verdicts = {}
    for lg in langs:
        real = per[f"{lg}:real"]["tune"]
        for cond in ("shufword", "shufchar"):
            sh = per[f"{lg}:{cond}"]["tune"]
            cmp = {}
            for name, key in (("fit", "fit_distances"), ("held", "held_distances")):
                p = float(mannwhitneyu(real[key], sh[key], alternative="two-sided").pvalue)
                cmp[name] = {"real": real[name], cond: sh[name], "p": p,
                             "real_better": bool(p < ALPHA and real[name] < sh[name]),
                             "shuffled_better": bool(p < ALPHA and sh[name] < real[name])}
            res["comparisons"][f"{lg}:{cond}"] = cmp
            print(f"{lg} real vs {cond}: fit {real['fit']:.2f} vs {sh['fit']:.2f} (p {cmp['fit']['p']:.1e}); "
                  f"held {real['held']:.2f} vs {sh['held']:.2f} (p {cmp['held']['p']:.1e})", flush=True)
        c = res["comparisons"][f"{lg}:shufchar"]
        real_b = c["fit"]["real_better"] or c["held"]["real_better"]
        shuf_b = c["fit"]["shuffled_better"] or c["held"]["shuffled_better"]
        verdicts[lg] = ("REAL FAVOURED" if real_b and not shuf_b else "SHUFFLED FAVOURED" if shuf_b and not real_b
                        else "MIXED" if real_b and shuf_b else "NOT DISTINGUISHABLE")
    n_real = sum(v == "REAL FAVOURED" for v in verdicts.values())
    res["per_language_verdict"] = verdicts
    res["verdict"] = ("MEANING DETECTABLE (real beats letter-shuffled in >= 3 of 4 languages)" if n_real >= 3 else
                      "MEANING NOT DETECTABLE by these statistics under this cipher model")
    res["wall_s"] = round(time.time() - t0)
    out_path = OUT if not a.smoke else ROOT / "experiments/results/smoke/e015_smoke.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=1, default=str))
    print(verdicts); print(res["verdict"])
    if not a.smoke:
        from vcl.eval.ledger import append
        append([dict(experiment="E015", model=f"naibbe_rep/{k}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                     split="voynich_DEV_fingerprint", metric=m, value=round(v["tune"][m2], 4), command=res["command"],
                     notes=f"pre-registered; {res['verdict'][:100]}")
                for k, v in res["conditions"].items() for m, m2 in (("fit_rms_z", "fit"), ("heldout_rms_z", "held"))])


if __name__ == "__main__":
    main()
