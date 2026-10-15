"""E007: can a real-language encoding AND a meaningless generator both be fitted to Voynich's fingerprint?

For each mechanism (positional_verbose over real plaintext in 6 languages; slot_grammar with no text) we random-
search parameters to minimise a standardised distance between its fingerprint and Voynich's (DEV leaves only,
EVA characters, 3,000-symbol windows). The noise floor is the distance between Voynich windows and the Voynich
mean. If both mechanisms reach the noise floor, the fingerprint cannot distinguish 'encoded language' from
'meaningless generator' -> report as an equivalence class (non-identifiable at this level of description).
Then: is the best-fitting LANGUAGE encoding solvable by solver v1 (known plaintext lets us check)?

Run: .venv/bin/python experiments/e007_identifiability.py [--trials 150]
"""
import argparse, importlib.util, json, random, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.solvers.features import features  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402
from vcl.synthetic.voynichlike import positional_verbose, slot_grammar  # noqa: E402

spec = importlib.util.spec_from_file_location("e006", ROOT / "experiments/e006_voynich_fingerprint.py")
e006 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e006)

KEYS = ["h1", "h_cond", "types", "ioc_x_types", "wl_mean", "wl_std", "word_ttr", "word_top_share",
        "init_entropy", "final_entropy", "never_init_mass", "double_rate"]
N = 3000
LANGS = ["la", "it", "de", "en", "fi", "tl"]


def vec(sym):
    f = features(sym[:N])
    return np.array([f[k] for k in KEYS])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--trials", type=int, default=150); a = ap.parse_args()
    rng = random.Random(7007)
    V = np.array([vec(w) for w in e006.voynich_windows(False)])
    mu, sd = V.mean(0), V.std(0) + 1e-6
    dist = lambda x: float(np.sqrt((((x - mu) / sd) ** 2).mean()))
    floor = float(np.median([dist(v) for v in V]))
    books = [b for b in load_books() if b["lang"] in LANGS]

    def plain_sample(r):
        b = r.choice(books)
        s = r.randrange(0, len(b["text"]) - 4000); s = b["text"].find(" ", s) + 1
        return b["text"][s:s + 2600].rsplit(" ", 1)[0], b

    best = {"positional_verbose": (1e9, None), "slot_grammar": (1e9, None)}
    trials = {"positional_verbose": [], "slot_grammar": []}
    for t in range(a.trials):
        r = random.Random(rng.randrange(2**31))
        p = dict(n_glyphs=r.randint(12, 26), p_two=r.uniform(0.1, 0.8), p_three=r.uniform(0, 0.25),
                 shared=r.uniform(0.0, 0.9))
        plain, b = plain_sample(r)
        sym = positional_verbose(plain, r, **p)[0]
        if len(sym) >= N:
            d = dist(vec(sym)); trials["positional_verbose"].append(d)
            if d < best["positional_verbose"][0]:
                best["positional_verbose"] = (d, {"params": p, "lang": b["lang"], "book": b["id"], "seed_state": t})
        q = dict(n_glyphs=r.randint(14, 26), n_prefix=r.randint(4, 25), n_core=r.randint(8, 60),
                 n_suffix=r.randint(4, 30), zipf=r.uniform(0.5, 1.6), p_empty=r.uniform(0.05, 0.6))
        sym = slot_grammar(N, r, **q)[0]
        d = dist(vec(sym)); trials["slot_grammar"].append(d)
        if d < best["slot_grammar"][0]:
            best["slot_grammar"] = (d, {"params": q, "seed_state": t})
    # stage 2: local refinement around each best (perturb parameters, keep improvements)
    def perturb(params, r, bounds):
        q = dict(params)
        k = r.choice(list(bounds))
        lo, hi = bounds[k]
        q[k] = (min(hi, max(lo, q[k] + r.choice([-2, -1, 1, 2])))) if isinstance(lo, int) else \
               min(hi, max(lo, q[k] + r.gauss(0, (hi - lo) * 0.1)))
        return q
    PVB = dict(n_glyphs=(10, 30), p_two=(0.0, 0.95), p_three=(0.0, 0.4), shared=(0.0, 0.95))
    SGB = dict(n_glyphs=(10, 30), n_prefix=(2, 40), n_core=(4, 90), n_suffix=(2, 40), zipf=(0.3, 2.0), p_empty=(0.0, 0.8))
    for t in range(a.trials):
        r = random.Random(rng.randrange(2**31))
        d0, info = best["positional_verbose"]
        p = perturb(info["params"], r, PVB)
        plain, b = plain_sample(r)
        if r.random() < 0.7:   # mostly stay with the best language, sometimes explore
            b = next(x for x in books if x["lang"] == info["lang"])
            s0 = r.randrange(0, len(b["text"]) - 4000); s0 = b["text"].find(" ", s0) + 1
            plain = b["text"][s0:s0 + 2600].rsplit(" ", 1)[0]
        sym = positional_verbose(plain, r, **p)[0]
        if len(sym) >= N:
            d = dist(vec(sym)); trials["positional_verbose"].append(d)
            if d < d0:
                best["positional_verbose"] = (d, {"params": p, "lang": b["lang"], "book": b["id"], "refine": t})
        d0, info = best["slot_grammar"]
        q = perturb(info["params"], r, SGB)
        d = dist(vec(slot_grammar(N, r, **q)[0])); trials["slot_grammar"].append(d)
        if d < d0:
            best["slot_grammar"] = (d, {"params": q, "refine": t})

    # direct check: word-length dispersion of plaintext in every language (no encoding needed)
    import statistics
    wl = {}
    for bk in load_books():
        ws = [len(w) for w in bk["text"][:200000].split(" ") if w]
        wl.setdefault(bk["lang"], []).append((statistics.mean(ws), statistics.pstdev(ws)))
    wl = {k: [round(statistics.mean(m for m, _ in v), 2), round(statistics.mean(s for _, s in v), 2)] for k, v in wl.items()}
    res_wl = {"plaintext_word_length_mean_sd_by_language": dict(sorted(wl.items(), key=lambda kv: kv[1][1])),
              "voynich_word_length_mean_sd": [round(float(mu[KEYS.index("wl_mean")]), 2), round(float(mu[KEYS.index("wl_std")]), 2)]}
    res = {"noise_floor_median_voynich_window_distance": round(floor, 3), "features": KEYS,
           "voynich_mean": dict(zip(KEYS, mu.round(3).tolist())), "trials": a.trials, "best": {}}
    for m in best:
        d, info = best[m]
        res["best"][m] = {"distance": round(d, 3), "within_noise_floor": d <= floor, "info": info,
                          "median_trial_distance": round(float(np.median(trials[m])), 3)}
        print(f"{m:20s} best distance {d:.3f} (noise floor {floor:.3f}) median {np.median(trials[m]):.3f}")
    res["word_length_dispersion"] = res_wl
    lo = min(v[1] for v in wl.values())
    print("min plaintext word-length sd over 36 languages:", lo, "voynich:", res_wl["voynich_word_length_mean_sd"])
    both = all(v["within_noise_floor"] for v in res["best"].values())
    res["verdict"] = ("NON-IDENTIFIABLE at fingerprint level: an encoding of real language and a meaningless "
                      "generator both reach Voynich's statistics within its own window-to-window variation."
                      if both else "Not both mechanisms reach the noise floor; see distances.")
    (ROOT / "experiments/results/e007.json").write_text(json.dumps(res, indent=1, default=str))
    print(res["verdict"])


if __name__ == "__main__":
    main()
