"""E019 (methodology test A1): what does one Voynich word carry -- a word, a syllable, or 1-2 letters?

Pre-registered in reports/E019_PREREG.md. Topic words cluster in a text ("burstiness"); letter pairs barely do.
So the burstiness of Voynich word types, compared with twins of each unit hypothesis built from the same sources,
tells us the unit size. Features (P = 32 equal chunks in reading order; types with >= 8 tokens):
  I_word   mean entropy deficit (bits) of a type's spread over chunks vs 5 shuffles (Montemurro-Zanette style)
  top_word share of types whose chunk counts are concentrated (chi-square p < 1e-3)
  I_sub / top_sub   the same for within-word glyph/letter bigrams (drift / copying signature; reported)
Families (10 samples per language for language families, 20 for generators), all at Voynich DEV size:
  word        plaintext words (unit = word; any substitution leaves this unchanged)
  syll        plaintext syllables (unit = syllable)
  naibbe      E014 best naibbe_rep spec (unit = 1-2 letters) on the same sources
  naibbe_max  same, but the 4 source segments come from 4 different LANGUAGES (upper bound for letter-level topic)
  rugg_rep, self_citation_rep   E014 best meaningless specs
Sources: 4 role tune+ref books per language (la, it, fr, de), 4 equal segments (one per book), Greshko-cleaned.

Run: caffeinate -ims .venv/bin/python experiments/e019_unit_burstiness.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, random, re, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 19019
PREREG = ROOT / "reports/E019_PREREG.md"
OUT = ROOT / "experiments/results/e019.json"
LANGS = ["la", "it", "fr", "de"]
FEATS = ["I_word", "top_word", "I_sub", "top_sub"]
WORD_FEATS = ["I_word", "top_word"]
P_CHUNKS, MIN_N, N_SHUF, Z_REJECT = 32, 8, 5, 4.0
G = {}


def _init(state):
    G.update(state)


def _H(v):
    p = v[v > 0] / v.sum()
    return float(-(p * np.log2(p)).sum())


def burst(tokens, P=P_CHUNKS, min_n=MIN_N):
    n = len(tokens)
    idx = (np.arange(n) * P) // n

    def per_type(toks):
        d = {}
        for t, c in zip(toks, idx):
            d.setdefault(t, np.zeros(P))[c] += 1
        return d
    real = per_type(tokens)
    keep = [t for t, v in real.items() if v.sum() >= min_n]
    shuf = []
    for s in range(N_SHUF):
        sh = list(tokens); random.Random(s).shuffle(sh); shuf.append(per_type(sh))
    num = den = 0.0
    top = 0
    for t in keep:
        v = real[t]
        num += v.sum() * (np.mean([_H(h[t]) for h in shuf]) - _H(v)); den += v.sum()
        e = v.sum() / P
        top += chi2.sf(float(((v - e) ** 2 / e).sum()), P - 1) < 1e-3
    return num / max(den, 1.0), top / max(1, len(keep)), len(keep)


def bigrams(tokens):
    return [w[i:i + 2] for w in tokens for i in range(len(w) - 1)]


def features(tokens):
    Iw, Tw, kw = burst(tokens)
    Is, Ts, ks = burst(bigrams(tokens))
    return {"I_word": Iw, "top_word": Tw, "I_sub": Is, "top_sub": Ts, "n_types": kw, "n_tokens": len(tokens)}


def syllables(w):
    parts = re.findall(r"[^aeiouy]*[aeiouy]+(?:[^aeiouy](?=[^aeiouy]))?|[^aeiouy]+$", w)
    return [p for p in parts if p] or [w]


def source_words(langs, n_total, rng):
    """One segment per book; `langs` lists the language of each of the 4 segments."""
    out, per = [], n_total // 4 + 1
    for i, lg in enumerate(langs):
        ws = G["books"][lg][i % len(G["books"][lg])]
        s = rng.randrange(0, max(1, len(ws) - per))
        out += ws[s:s + per]
    return out[:n_total]


def generate(fam, lg, seed, N):
    rng = random.Random(seed)
    if fam == "word":
        return source_words([lg] * 4, N, rng)
    if fam == "syll":
        out = []
        for w in source_words([lg] * 4, N, rng):
            out += syllables(w)
        return out[:N]
    if fam in ("naibbe", "naibbe_max"):
        src = [lg] * 4 if fam == "naibbe" else LANGS
        plain = " ".join(source_words(src, 14000, rng))
        spec = G["e14"].get(("naibbe_rep", lg), G["e14"][("naibbe_rep", "la")])
        g = R.generate("naibbe_rep", spec, seed, G["pools"], N, G["C"], G["nulls"], plain=plain)
        return [w for l in g["lines"] for w in l if w][:N]
    g = R.generate(fam, G["e14"][(fam, None)], seed, G["pools"], N, G["C"], G["nulls"])
    return [w for l in g["lines"] for w in l if w][:N]


def run(task):
    fam, lg, seed, N = task
    toks = generate(fam, lg, seed, N)
    return {"family": fam, "lang": lg, "seed": seed, "N": N, **features(toks)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    lines, cur, dev_words, _ = E.voynich_lines()
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = {}
    for b in load_books():
        if b["lang"] in LANGS and roles.get(b["id"], {}).get("role") in ("tune", "ref"):
            books.setdefault(b["lang"], []).append([w for w in (NX.clean(x) for x in b["text"][2000:].split()) if w])
    e14 = {(c["family"], c["lang"]): c["params"]
           for c in json.loads((ROOT / "experiments/results/e014.json").read_text())["combos"]}
    state = {"books": books, "e14": e14, "C": X.coupling_matrix(lines), "nulls": R.null_pool(dev_words),
             "pools": T.chunk_pools(dev_words)}
    vdev = [w for l in lines for w in l if w]
    vB = [w for l, c in zip(lines, cur) if c == "B" for w in l if w]
    sizes = {"DEV": len(vdev), "B": len(vB)}
    n_lang, n_gen = (10, 20) if not a.smoke else (1, 1)
    fams = ["word", "syll", "naibbe", "naibbe_max", "rugg_rep", "self_citation_rep"]
    rng = random.Random(SEED)
    tasks = []
    for part, N in sizes.items():
        if a.smoke and part == "B":
            continue
        for f in fams:
            if f in ("rugg_rep", "self_citation_rep"):
                tasks += [(f, None, rng.randrange(2 ** 31), N) for _ in range(n_gen)]
            else:
                tasks += [(f, lg, rng.randrange(2 ** 31), N) for lg in LANGS for _ in range(n_lang)]
    print(len(tasks), "twin samples", sizes, flush=True)
    with Pool(a.workers, initializer=_init, initargs=(state,)) as pool:
        twins = list(pool.imap_unordered(run, tasks))
    res = {"experiment": "e019", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha, "seed": SEED,
           "command": " ".join(sys.argv), "sizes": sizes, "twins": twins, "parts": {}}
    # Voynich is measured only after every twin exists
    for part, toks in (("DEV", vdev), ("B", vB)):
        if a.smoke and part == "B":
            continue
        v = features(toks)
        fam_out = {}
        for f in fams:
            rows = [t for t in twins if t["family"] == f and t["N"] == sizes[part]]
            mu = {k: float(np.mean([r[k] for r in rows])) for k in FEATS}
            sd = {k: max(float(np.std([r[k] for r in rows], ddof=1)) if len(rows) > 1 else 0.0, 0.01) for k in FEATS}
            z = {k: (v[k] - mu[k]) / sd[k] for k in FEATS}
            counted = [k for k in WORD_FEATS if abs(z[k]) > Z_REJECT and not (f == "word" and z[k] > 0)]
            fam_out[f] = {"mean": mu, "sd": sd, "range": {k: [min(r[k] for r in rows), max(r[k] for r in rows)]
                                                         for k in FEATS},
                          "z": z, "rms_z": float(np.sqrt(np.mean([z[k] ** 2 for k in FEATS]))),
                          "rejected": bool(counted), "rejected_on": counted}
        surv = [f for f in fams if not fam_out[f]["rejected"]]
        res["parts"][part] = {"voynich": v, "families": fam_out, "surviving": surv,
                              "favoured": min(fams, key=lambda f: fam_out[f]["rms_z"])}
        print(part, {k: round(v[k], 4) for k in FEATS}, flush=True)
        for f in fams:
            o = fam_out[f]
            print(f"  {f:18s} rms_z {o['rms_z']:6.2f} z " + " ".join(f"{k} {o['z'][k]:+.1f}" for k in FEATS)
                  + ("  REJECTED" if o["rejected"] else ""), flush=True)
        print("  surviving", surv, "favoured", res["parts"][part]["favoured"], flush=True)
    res["wall_s"] = round(time.time() - t0)
    out = OUT if not a.smoke else ROOT / "experiments/results/smoke/e019_smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str))
    if not a.smoke:
        from vcl.eval.ledger import append
        d = res["parts"]["DEV"]
        append([dict(experiment="E019", model=f"unit_family/{f}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                     split="voynich_DEV_burstiness", metric="rms_z", value=round(d["families"][f]["rms_z"], 3),
                     command=res["command"], notes="REJECTED" if d["families"][f]["rejected"] else "survives")
                for f in fams])


if __name__ == "__main__":
    main()
