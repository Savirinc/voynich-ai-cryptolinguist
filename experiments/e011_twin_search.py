"""E011: Voynich twins -- which mechanism families can reproduce Voynich's fingerprint? (STRUCTURAL ONLY)

Families (src/vcl/synthetic/twins.py): naibbe (Naibbe-style verbose homophonic table cipher, approximation of
Greshko 2025), abbreviation (medieval-style shorthand + glyph mapping), syllabary -- all encode real plaintext and
are exactly decodable -- and two meaningless generators: rugg_grille (Rugg 2004) and self_citation (Timm & Schinner
2019/20). All emit EVA words built from the same DEV-derived glyph-chunk pools and the same line-wrapping rule.

Design
  * Target: Voynich DEV leaves only (LOCKED_TEST untouched), prose, clean tokens, lines in manuscript order, cut into
    blocks of ~BLOCK symbols at line boundaries. Fingerprint per block = e006/e007 window features (mean over four
    3,000-symbol windows) + block-level word/line statistics.
  * FIT features (used by the search) and HELD-OUT features (never seen by the search) are disjoint lists below.
    Line-position effects (y->q, line-final m vs iin, q->o) are held out: no family has a line mechanism.
  * Standardisation: per-feature SD across Voynich DEV blocks (floored at 2% of |mean|). Distance = RMS z.
    Noise floor = median leave-one-out distance of a Voynich block to the mean of the other blocks.
  * Search per family x source language: random search then local refinement (perturb-the-best), one sampled block
    per evaluation, plaintext from role=tune books. Decoy families get 3x the per-language budget.
  * Final evaluation: best spec of each combo regenerated N_FINAL times with fresh seeds on tune text, and N_FINAL
    times on role=ref books (held-out TEXT). Unbiased by the search's winner's curse.
  * Identifiability: (a) held-out distance of best meaningful vs best meaningless (Mann-Whitney); (b) a grouped-CV
    logistic classifier meaningful-vs-meaningless on held-out features, and where Voynich blocks fall.
  * Currier A vs B: distance between A-block and B-block means, as a scale for "how different is different".
Run: caffeinate -ims .venv/bin/python experiments/e011_twin_search.py [--scale 1.0] [--smoke]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
from vcl.solvers.features import features  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402
from vcl.synthetic.schema import BOUNDARY  # noqa: E402

SEED = 11011
BLOCK = 12000
WIN = 3000
LANGS = ["la", "it", "de", "enm", "fr", "es", "cs", "he"]
LANG_FAMS = ["naibbe", "abbreviation", "syllabary"]
DECOY_FAMS = ["rugg_grille", "self_citation"]
FIT = ["h1", "h_cond", "types", "ioc_x_types", "wl_mean", "wl_cv", "word_ttr", "init_entropy", "final_entropy",
       "never_init_mass"]
HELD = ["double_rate", "word_top_share", "wl_1", "h3_cond", "type_hapax", "zipf_slope", "adj_repeat", "ed1_types",
        "yq_logor", "mfinal_logor", "qo_share"]
WINDOW_KEYS = ["h1", "h_cond", "types", "ioc_x_types", "word_ttr", "init_entropy", "final_entropy",
               "never_init_mass", "double_rate", "word_top_share", "wl_1"]
# English function words that are not also common words of the target languages (Czech "to", Hebrew-free)
ENGLISH = set("the and of is that which with his was for as be by this not are from".split())
OUT = ROOT / "experiments/results/e011.json"
SPECS = ROOT / "data/derived/twins_v1/specs.json"


# ------------------------------------------------------------------------------------------------ fingerprint
def _ent(c):
    a = np.array([v for v in c.values() if v > 0], float)
    if a.sum() == 0:
        return 0.0
    p = a / a.sum()
    return float(-(p * np.log2(p)).sum())


def _ed1_share(types):
    """Share of word types with another type at edit distance 1 (deletion, insertion or substitution)."""
    ts = set(types)
    dels = defaultdict(set)
    for t in ts:
        for i in range(len(t)):
            dels[(i, t[:i] + t[i + 1:])].add(t)
    deleted_forms = {v for (_, v) in dels}          # t is a deletion of some other type -> insertion neighbour
    hit = 0
    for t in ts:
        hit += t in deleted_forms or any((t[:i] + t[i + 1:]) in ts or len(dels[(i, t[:i] + t[i + 1:])]) > 1
                                         for i in range(len(t)))
    return hit / max(1, len(ts))


def fingerprint(lines: list[list]) -> dict:
    """lines: list of lists of EVA word strings (None = unreadable word, kept as an adjacency break)."""
    words = [w for l in lines for w in l if w]
    sym = []
    for w in words:
        if sym:
            sym.append(BOUNDARY)
        sym.extend(w)
    f = {}
    wins = [features(sym[i:i + WIN]) for i in range(0, len(sym) - WIN + 1, WIN)][:4]
    for k in WINDOW_KEYS:
        f[k] = float(np.mean([w[k] for w in wins]))
    wl = np.array([len(w) for w in words], float)
    f["wl_mean"] = float(wl.mean()); f["wl_cv"] = float(wl.std() / wl.mean())
    big, tri = Counter(zip(sym, sym[1:])), Counter(zip(sym, sym[1:], sym[2:]))
    f["h3_cond"] = _ent(tri) - _ent(big)
    wc = Counter(words)
    f["type_hapax"] = sum(1 for v in wc.values() if v == 1) / len(wc)
    fr = np.array(sorted(wc.values(), reverse=True)[:100], float)
    r = np.arange(1, len(fr) + 1)
    f["zipf_slope"] = float(np.polyfit(np.log(r), np.log(fr), 1)[0]) if len(fr) > 2 else 0.0
    rep = n = 0
    yq = [0, 0, 0, 0]; mt = [0, 0, 0, 0]; q = qo = 0
    for l in lines:
        for a, b in zip(l, l[1:]):
            if a is None or b is None:
                continue
            n += 1; rep += a == b
            yq[(0 if a.endswith("y") else 2) + (0 if b.startswith("q") else 1)] += 1
        for i, w in enumerate(l):
            if w is None:
                continue
            row = 0 if w.endswith("m") else (2 if w.endswith("iin") else None)
            if row is not None:
                mt[row + (0 if i == len(l) - 1 else 1)] += 1
            if w.startswith("q"):
                q += 1; qo += w[1:2] == "o"
    lor = lambda a, b, c, d: math.log(((a + .5) * (d + .5)) / ((b + .5) * (c + .5)))
    f["adj_repeat"] = rep / max(1, n)
    f["yq_logor"] = lor(*yq); f["mfinal_logor"] = lor(*mt)
    f["qo_share"] = qo / q if q else 0.0
    f["ed1_types"] = _ed1_share(list(wc))
    f["n_words"] = len(words); f["n_lines"] = len(lines)
    return f


def cut_blocks(lines, size=BLOCK, tags=None):
    """Cut a list of lines into consecutive blocks of >= size symbols at line boundaries."""
    out, cur, n, ctags = [], [], 0, []
    for i, l in enumerate(lines):
        cur.append(l); n += sum(len(w) + 1 for w in l if w)
        if tags is not None:
            ctags.append(tags[i])
        if n >= size:
            out.append((cur, Counter(ctags).most_common(1)[0][0] if ctags else None)); cur, n, ctags = [], 0, []
    return out


def voynich_lines():
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    L, cur = defaultdict(list), {}
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t.eva if t.is_clean else None)
            cur[(t.folio, t.line_no)] = t.currier
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    lines = [L[k] for k in order]
    dev_words = [t.eva for t in toks if t.mode == "prose" and t.is_clean and t.leaf not in locked]
    assert not ({t.leaf for t in toks if t.mode == "prose" and t.leaf not in locked} & locked)
    return lines, [cur[k] for k in order], dev_words, sorted(locked, key=lambda x: (len(x), x))


# ------------------------------------------------------------------------------------------------ plaintext
def _clean_chunk(text, lang):
    ws = text.split(" ")
    if lang not in ("en", "enm") and sum(w in ENGLISH for w in ws) / max(1, len(ws)) > 0.015:
        return False
    letters = [c for c in text if c != " "]
    if lang == "he":
        return sum("֐" <= c <= "׿" for c in letters) / len(letters) > 0.97
    return sum(ord(c) < 0x250 for c in letters) / len(letters) > 0.97


def plain_chunks(books, lang, role, size=24000, step=12000):
    out = []
    for b in books:
        if b["lang"] != lang or b["role"] != role:
            continue
        t = b["text"]
        for s in range(2000, len(t) - size, step):   # skip the first 2,000 chars (front matter)
            s2 = t.find(" ", s) + 1
            ch = t[s2:s2 + size].rsplit(" ", 1)[0]
            if _clean_chunk(ch, lang):
                out.append((b["id"], s2, ch))
    return out


# ------------------------------------------------------------------------------------------------ worker
G = {}


def _init(state):
    G.update(state)


def sample_fp(family, params, seed, chunk=None):
    n_words = int(BLOCK / 5.0 * 1.4)
    g = T.generate(family, params, seed, G["pools"], n_words, plain=chunk, width_mean=G["width"][0],
                   width_sd=G["width"][1])
    blocks = cut_blocks(g["lines"])
    if not blocks:
        return None
    return fingerprint(blocks[0][0])


def dist(f, keys):
    if f is None:
        return 1e9
    z = [(f[k] - G["mu"][k]) / G["sd"][k] for k in keys]
    return float(np.sqrt(np.mean(np.square(z))))


def search_combo(task):
    family, lang, n_rand, n_ref, seed = task
    rng = random.Random(seed)
    chunks = G["chunks"].get((lang, "tune"), [None])
    t0 = time.time()
    trace, best = [], (1e9, None, None)
    for i in range(n_rand + n_ref):
        if i < n_rand or best[1] is None:
            p = T.random_params(family, rng)
        else:
            p = T.perturb_params(family, best[1], rng, scale=0.15 if i < n_rand + n_ref // 2 else 0.07)
        ch = rng.choice(chunks)
        s = rng.randrange(2 ** 31)
        try:
            f = sample_fp(family, p, s, ch[2] if ch else None)
        except Exception as ex:  # noqa: BLE001 - a bad parameter corner must not kill the search
            f = None
        d = dist(f, FIT)
        trace.append(round(d, 4))
        if d < best[0]:
            best = (d, p, {"seed": s, "book": ch[0] if ch else None, "offset": ch[1] if ch else None})
    return {"family": family, "lang": lang, "best_search_distance": best[0], "params": best[1],
            "best_sample": best[2], "n_evals": len(trace), "median_trial": float(np.median(trace)),
            "wall_s": round(time.time() - t0, 1)}


def final_eval(task):
    family, lang, params, n, seed = task
    rng = random.Random(seed)
    out = {}
    for role in (["tune", "ref"] if lang else ["none"]):
        chunks = G["chunks"].get((lang, role), []) if lang else [None]
        fps = []
        for _ in range(n):
            ch = rng.choice(chunks) if chunks else None
            if lang and ch is None:
                break
            f = sample_fp(family, params, rng.randrange(2 ** 31), ch[2] if ch else None)
            if f is not None:
                fps.append(f)
        out[role] = fps
    return family, lang, out


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--reuse-search", action="store_true",
                    help="keep the searched parameters in experiments/results/e011.json; redo final eval + analysis")
    a = ap.parse_args()
    t_start = time.time()
    n_rand, n_ref, n_final = (int(140 * a.scale), int(160 * a.scale), 20) if not a.smoke else (4, 4, 3)
    langs = LANGS if not a.smoke else ["la", "it"]

    lines, cur, dev_words, locked = voynich_lines()
    pools = T.chunk_pools(dev_words)
    lens = [sum(len(w) for w in l if w) + len([w for w in l if w]) - 1 for l in lines if any(l)]
    width = (float(np.mean(lens)), float(np.std(lens)))
    vb = cut_blocks(lines, tags=cur)
    VF = [fingerprint(b) for b, _ in vb]
    keys = FIT + HELD
    M = np.array([[f[k] for k in keys] for f in VF])
    mu = dict(zip(keys, M.mean(0))); sd = dict(zip(keys, np.maximum(M.std(0, ddof=1), 0.02 * np.abs(M.mean(0)) + 1e-3)))

    def zd(f, ks, m=mu):
        return float(np.sqrt(np.mean([((f[k] - m[k]) / sd[k]) ** 2 for k in ks])))
    loo = {}
    for name, ks in (("fit", FIT), ("held", HELD), ("all", keys)):
        ds = []
        for i in range(len(VF)):
            m_i = {k: np.mean([VF[j][k] for j in range(len(VF)) if j != i]) for k in ks}
            ds.append(zd(VF[i], ks, m_i))
        loo[name] = {"median": float(np.median(ds)), "p90": float(np.percentile(ds, 90))}
    # Currier A vs B (lines tagged by page language)
    ab = {}
    for c in "AB":
        idx = [i for i, x in enumerate(cur) if x == c]
        bl = cut_blocks([lines[i] for i in idx])
        ab[c] = [fingerprint(b) for b, _ in bl]
    ab_mean = {c: {k: float(np.mean([f[k] for f in ab[c]])) for k in keys} for c in "AB"}
    currier = {"n_blocks": {c: len(ab[c]) for c in "AB"},
               "A_vs_B_distance_fit": zd(ab_mean["A"], FIT, ab_mean["B"]),
               "A_vs_B_distance_held": zd(ab_mean["A"], HELD, ab_mean["B"]),
               "A_mean": {k: round(v, 4) for k, v in ab_mean["A"].items()},
               "B_mean": {k: round(v, 4) for k, v in ab_mean["B"].items()}}
    print(f"Voynich DEV blocks {len(VF)}; floors {loo}; width {width}; A/B fit {currier['A_vs_B_distance_fit']:.2f}"
          f" held {currier['A_vs_B_distance_held']:.2f}", flush=True)

    books = [b | {"role": json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
                  .get(b["id"], {}).get("role")} for b in load_books() if b["lang"] in langs]
    chunks = {}
    for lg in langs:
        for role in ("tune", "ref"):
            chunks[(lg, role)] = plain_chunks(books, lg, role)
    chunk_info = {f"{lg}/{r}": {"n_chunks": len(v), "books": sorted({c[0] for c in v})} for (lg, r), v in chunks.items()}
    print("plaintext chunks:", {k: v["n_chunks"] for k, v in chunk_info.items()}, flush=True)
    state = {"pools": pools, "width": width, "mu": mu, "sd": sd, "chunks": chunks}

    rng = random.Random(SEED)
    tasks = [(fam, lg, n_rand, n_ref, rng.randrange(2 ** 31)) for fam in LANG_FAMS for lg in langs]
    tasks += [(fam, None, 3 * n_rand, 3 * n_ref, rng.randrange(2 ** 31)) for fam in DECOY_FAMS]
    tasks.sort(key=lambda t: -(t[2] + t[3]))   # long decoy searches first
    prev = json.loads(OUT.read_text()) if a.reuse_search else None
    with Pool(a.workers, initializer=_init, initargs=(state,)) as pool:
        searched = []
        if prev:
            for c in prev["combos"]:
                searched.append({"family": c["family"], "lang": c["lang"], "params": c["params"], **c["search"]})
            tasks = []
            t_prev_search = prev["wall_s"]["search"]
        for r in pool.imap_unordered(search_combo, tasks):
            searched.append(r)
            print(f"  search {r['family']:13s} {str(r['lang']):4s} best {r['best_search_distance']:.3f} "
                  f"median {r['median_trial']:.2f} ({r['n_evals']} evals, {r['wall_s']} s)", flush=True)
        t_search = (time.time() - t_start) if not prev else t_prev_search
        ftasks = [(r["family"], r["lang"], r["params"], n_final, rng.randrange(2 ** 31)) for r in searched]
        finals = {}
        for fam, lg, out in pool.imap_unordered(final_eval, ftasks):
            finals[(fam, lg)] = out
    _init(state)

    # ---------------------------------------------------------------- per combo summaries
    combos = []
    for r in searched:
        out = finals[(r["family"], r["lang"])]
        main_role = "tune" if r["lang"] else "none"
        fps = out[main_role]
        mean_f = {k: float(np.mean([f[k] for f in fps])) for k in keys}
        z = {k: round((mean_f[k] - mu[k]) / sd[k], 2) for k in keys}
        c = {"family": r["family"], "lang": r["lang"], "is_language": T.FAMILIES[r["family"]].is_language,
             "params": r["params"], "search": {k: r[k] for k in ("best_search_distance", "median_trial", "n_evals",
                                                                 "wall_s", "best_sample")},
             "reeval_n": len(fps),
             "fit_distance": float(np.mean([dist(f, FIT) for f in fps])),
             "fit_distance_sd": float(np.std([dist(f, FIT) for f in fps])),
             "held_distance": float(np.mean([dist(f, HELD) for f in fps])),
             "held_distance_sd": float(np.std([dist(f, HELD) for f in fps])),
             "held_distances": [round(dist(f, HELD), 4) for f in fps],
             "held_z_samples": [[round((f[k] - mu[k]) / sd[k], 3) for k in HELD] for f in fps],
             "z_per_feature": z,
             "features_matched_abs_z_lt_2": [k for k in keys if abs(z[k]) < 2],
             "features_missed": [k for k in keys if abs(z[k]) >= 2],
             "mean_fingerprint": {k: round(v, 4) for k, v in mean_f.items()}}
        if r["lang"]:
            ref = out.get("ref", [])
            c["heldout_text"] = {"n": len(ref),
                                 "fit_distance": float(np.mean([dist(f, FIT) for f in ref])) if ref else None,
                                 "held_distance": float(np.mean([dist(f, HELD) for f in ref])) if ref else None}
        c["_fps"] = fps
        combos.append(c)
    combos.sort(key=lambda c: c["fit_distance"])

    best_by_family = {}
    for c in combos:
        best_by_family.setdefault(c["family"], c)

    # ---------------------------------------------------------------- identifiability
    from scipy.stats import mannwhitneyu
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.metrics import roc_auc_score
    mean_fams = [best_by_family[f] for f in LANG_FAMS if f in best_by_family]
    dec_fams = [best_by_family[f] for f in DECOY_FAMS if f in best_by_family]
    bm = min(mean_fams, key=lambda c: c["fit_distance"]); bd = min(dec_fams, key=lambda c: c["fit_distance"])
    mw = mannwhitneyu(bm["held_distances"], bd["held_distances"], alternative="two-sided")
    floor_f, floor_h = loo["fit"]["median"], loo["held"]["median"]

    def zmat(fps, ks):
        return np.array([[(f[k] - mu[k]) / sd[k] for k in ks] for f in fps])
    clf_res = {}
    for name, ks in (("held_out_features", HELD), ("all_features", keys)):
        X, y, g = [], [], []
        for gi, c in enumerate(mean_fams + dec_fams):
            Z = zmat(c["_fps"], ks); X.append(Z); y += [int(c["is_language"])] * len(Z); g += [gi] * len(Z)
        X = np.vstack(X); y = np.array(y); g = np.array(g)
        # grouped CV by family: train on the other families -> tests whether 'meaningful vs meaningless' is a
        # property that transfers across mechanisms (leave-one-family-out)
        pred = np.zeros(len(y))
        for tr, te in GroupKFold(len(set(g))).split(X, y, g):
            if len(set(y[tr])) < 2:
                pred[te] = 0.5; continue
            m = LogisticRegression(C=1.0, max_iter=2000).fit(X[tr], y[tr]); pred[te] = m.predict_proba(X[te])[:, 1]
        m = LogisticRegression(C=1.0, max_iter=2000).fit(X, y)
        within = LogisticRegression(C=1.0, max_iter=2000)
        # in-sample separability (pooled 5-fold, not grouped): can the twins be told apart at all?
        from sklearn.model_selection import cross_val_predict, StratifiedKFold
        pin = cross_val_predict(within, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                                method="predict_proba")[:, 1]
        pv = m.predict_proba(zmat(VF, ks))[:, 1]
        clf_res[name] = {"auc_pooled_5fold": round(float(roc_auc_score(y, pin)), 3),
                         "auc_leave_one_family_out": round(float(roc_auc_score(y, pred)), 3),
                         "voynich_blocks_p_meaningful_mean": round(float(pv.mean()), 3),
                         "voynich_blocks_p_meaningful_range": [round(float(pv.min()), 3), round(float(pv.max()), 3)]}

    within_f = [c for c in combos if c["fit_distance"] <= loo["fit"]["p90"]]
    held_nohap = [k for k in HELD if k != "type_hapax"]
    pairs = {}
    for d in dec_fams:
        for name, ks in (("held", HELD), ("held_without_type_hapax", held_nohap)):
            a1 = [dist(f, ks) for f in bm["_fps"]]; a2 = [dist(f, ks) for f in d["_fps"]]
            pairs[f"{bm['family']}/{bm['lang']} vs {d['family']} [{name}]"] = {
                "mean_meaningful": round(float(np.mean(a1)), 3), "mean_meaningless": round(float(np.mean(a2)), 3),
                "mannwhitney_p": float(mannwhitneyu(a1, a2, alternative="two-sided").pvalue)}
    for c in combos:
        c["held_distance_without_type_hapax"] = float(np.mean([dist(f, held_nohap) for f in c["_fps"]]))
    best_held_overall = min(combos, key=lambda c: c["held_distance"])
    ranking = [f"{c['family']}/{c['lang']}" for c in sorted(best_by_family.values(), key=lambda c: c["fit_distance"])]
    any_twin = bool(within_f)
    robust = all(v["mannwhitney_p"] < 0.01 and v["mean_meaningful"] < v["mean_meaningless"] for v in pairs.values())
    same = all(v["mannwhitney_p"] >= 0.01 for v in pairs.values())
    if not any_twin:
        head = (f"NO TWIN: none of the five families reaches Voynich's own block-to-block variation on the fit "
                f"features (best {bm['family']}/{bm['lang']} {bm['fit_distance']:.2f} vs floor median "
                f"{loo['fit']['median']:.2f}, p90 {loo['fit']['p90']:.2f}). Identifiability between meaningful and "
                "meaningless mechanisms therefore cannot be established or refuted at the level of an exact twin. ")
    else:
        names = [c["family"] + "/" + str(c["lang"]) for c in within_f]
        head = f"TWINS FOUND within the fit-feature noise floor (p90): {names}. "
    if robust:
        tail = ("Among the best fits, the meaningful (Naibbe-style) twin is closer to Voynich than every meaningless "
                "generator on held-out features, also without the dominant type-hapax feature -> the families are "
                "distinguishable and this ranking favours a verbose-cipher mechanism over the two hoax mechanisms "
                "tested. It ranks approximations; it is not a decipherment.")
    elif same:
        tail = "Held-out features do not separate the best meaningful from the best meaningless twins (non-identifiable)."
    else:
        tail = "Held-out comparisons are mixed (see pairwise table); no robust separation."
    verdict = head + tail
    ident = {"best_meaningful": f"{bm['family']}/{bm['lang']}", "best_meaningless": bd["family"],
             "best_meaningful_fit": round(bm["fit_distance"], 3), "best_meaningless_fit": round(bd["fit_distance"], 3),
             "best_meaningful_held": round(bm["held_distance"], 3),
             "best_meaningless_held": round(bd["held_distance"], 3),
             "mannwhitney_held_p": float(mw.pvalue), "pairwise_heldout": pairs,
             "best_held_out_combo": f"{best_held_overall['family']}/{best_held_overall['lang']}",
             "ranking_by_fit_distance_best_per_family": ranking,
             "classifier": clf_res,
             "classifier_caveat": ("pooled AUC measures whether twin families can be told apart from each other; "
                                   "leave-one-family-out AUC measures whether a 'language vs non-language' boundary "
                                   "transfers to an unseen mechanism. If the latter is <= 0.5 the Voynich probability "
                                   "is not interpretable and is not used in the verdict."),
             "combos_within_fit_p90_floor": [f"{c['family']}/{c['lang']}" for c in within_f],
             "verdict": verdict}

    res = {"experiment": "E011", "seed": SEED, "command": " ".join(["caffeinate -ims .venv/bin/python"] + sys.argv),
           "protocol": "eval/PROTOCOL_v1.md; Voynich DEV leaves only; LOCKED_TEST leaves excluded: " + ",".join(locked),
           "block_symbols": BLOCK, "window_symbols": WIN, "fit_features": FIT, "held_out_features": HELD,
           "voynich": {"n_blocks": len(VF), "mean": {k: round(float(v), 4) for k, v in mu.items()},
                       "sd": {k: round(float(v), 4) for k, v in sd.items()}, "noise_floor_loo": loo,
                       "line_width_glyphs_mean_sd": width, "currier": currier},
           "plaintext": chunk_info, "budget": {"n_random": n_rand, "n_refine": n_ref, "decoy_multiplier": 3,
                                               "n_final_regenerations": n_final, "workers": a.workers},
           "families": {f: {"is_language": T.FAMILIES[f].is_language, "citation": T.FAMILIES[f].citation,
                            "citation_status": T.FAMILIES[f].citation_status} for f in LANG_FAMS + DECOY_FAMS},
           "combos": [{k: v for k, v in c.items() if k != "_fps"} for c in combos],
           "best_by_family": {f: {k: v for k, v in c.items() if k not in ("_fps", "held_distances", "held_z_samples")}
                              for f, c in best_by_family.items()},
           "identifiability": ident,
           "wall_s": {"search": round(t_search, 1), "total": round(time.time() - t_start, 1)}}
    if not a.smoke:
        OUT.write_text(json.dumps(res, indent=1, default=float))
        SPECS.parent.mkdir(parents=True, exist_ok=True)
        specs = {"version": "twins_v1", "created_by": "experiments/e011_twin_search.py", "seed": SEED,
                 "usage": ("from vcl.synthetic.twins import generate; generate(spec['family'], spec['params'], seed, "
                           "pools, n_words, plain=<normalised text of a book in spec['plaintext_books']>, "
                           "width_mean=layout[0], width_sd=layout[1]) -> lines + key (+ plaintext). Use role=tune/ref "
                           "books only; never role=test for tuning."),
                 "pools": pools, "layout_line_width_mean_sd": width,
                 "specs": [{"family": c["family"], "lang": c["lang"], "is_language": c["is_language"],
                            "params": c["params"], "fit_distance": round(c["fit_distance"], 4),
                            "held_distance": round(c["held_distance"], 4),
                            "plaintext_books": chunk_info.get(f"{c['lang']}/tune", {}).get("books") if c["lang"] else None,
                            "heldout_text_books": chunk_info.get(f"{c['lang']}/ref", {}).get("books") if c["lang"] else None}
                           for c in combos]}
        SPECS.write_text(json.dumps(specs, indent=1, ensure_ascii=False))
        from vcl.eval.ledger import append
        rows = []
        for f, c in best_by_family.items():
            for metric, val in (("fit_distance", c["fit_distance"]), ("held_out_distance", c["held_distance"])):
                rows.append({"experiment": "E011", "model": f"twin:{f}/{c['lang']}", "split": "voynich_DEV",
                             "metric": metric, "value": round(val, 4), "command": res["command"],
                             "notes": f"rms z vs Voynich DEV blocks; floor fit {floor_f:.3f} held {floor_h:.3f}; "
                                      f"n={c['reeval_n']} regenerations; seed {SEED}"
                                      + ("; REANALYSIS (--reuse-search): same searched params, fresh final eval"
                                         if prev else "")})
        rows.append({"experiment": "E011", "model": "identifiability", "split": "voynich_DEV",
                     "metric": "mannwhitney_p_heldout_best_meaningful_vs_best_meaningless", "value": f"{mw.pvalue:.4g}",
                     "command": res["command"], "notes": verdict[:180]})
        append(rows)
    print(json.dumps({"floors": loo, "ident": ident, "best": {f: (c["lang"], round(c["fit_distance"], 3),
                      round(c["held_distance"], 3)) for f, c in best_by_family.items()}}, indent=1, default=float))
    print("wall", round(time.time() - t_start, 1), "s")


if __name__ == "__main__":
    main()
