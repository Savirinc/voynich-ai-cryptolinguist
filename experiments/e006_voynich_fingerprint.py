"""E006: Voynich writing-system hypothesis ranking by statistical fingerprint (STRUCTURAL ONLY, Gate 4 level).

Question: which known-answer mechanisms (13 encoders x 36 languages, plain text, 4 nonlinguistic generators)
produce symbol streams whose fingerprint resembles Voynichese? This ranks hypotheses; it decodes nothing and
makes no semantic claim. Solvers are NOT applied to Voynich (Gate 1 is PARTIAL -> decoding runs would be VOID).

Design
  * Reference set: freshly generated streams of ~N_SYM symbols from ref/tune/test books of ALL families, every
    encoder, raw plaintext ('plain'), and decoys (markov from a mono cipher, autocopy, grille, zipf_bag).
  * Positive control: grouped CV (group = source book) fingerprint classifier accuracy per class.
  * Voynich: windows of N_SYM symbols from DEV leaves only (LOCKED_TEST untouched), prose, clean tokens,
    two segmentations: EVA characters, and EVA with common multi-glyph units fused (ch, sh, cth, ckh, cph, cfh,
    iin, ii, ee). Report class probabilities and a typicality check (distance percentile within each class).
Run: .venv/bin/python experiments/e006_voynich_fingerprint.py
"""
import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
from vcl.solvers.features import feature_vector  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402
from vcl.synthetic.decoys import DECOYS  # noqa: E402
from vcl.synthetic.encoders import ENCODERS  # noqa: E402
from vcl.synthetic.schema import BOUNDARY  # noqa: E402

N_SYM = 3000
PER_CLASS = 60
SEED = 6006
UNITS = ["cth", "ckh", "cph", "cfh", "iin", "ch", "sh", "ii", "ee"]


def voynich_windows(fuse: bool):
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    lines = defaultdict(list)
    for t in toks:
        if t.mode == "prose" and t.is_clean and t.leaf not in locked:
            lines[(t.folio, t.line_no)].append(t.eva)
    stream = []
    for _, ws in sorted(lines.items(), key=lambda kv: (int(''.join(c for c in kv[0][0] if c.isdigit()) or 0), kv[0])):
        for w in ws:
            if stream:
                stream.append(BOUNDARY)
            if fuse:
                i, units = 0, []
                while i < len(w):
                    u = next((u for u in UNITS if w.startswith(u, i)), w[i])
                    units.append(u); i += len(u)
                stream.extend(units)
            else:
                stream.extend(list(w))
    # non-overlapping windows starting at word boundaries
    out, i = [], 0
    while i + N_SYM <= len(stream):
        out.append(stream[i:i + N_SYM]); i += N_SYM
    return out


def reference(rng):
    books = load_books()
    X, y, g = [], [], []
    by_family = defaultdict(list)
    for b in books:
        by_family[b["family"]].append(b)
    fams = sorted(by_family)

    def sample_plain(n_chars):
        fam = fams[rng.randrange(len(fams))]
        b = rng.choice(by_family[fam])
        s = rng.randrange(0, max(1, len(b["text"]) - n_chars - 10))
        s = b["text"].find(" ", s) + 1
        return b["text"][s:s + n_chars].rsplit(" ", 1)[0], b["id"]

    def add(sym, label, group):
        if len(sym) >= N_SYM:
            X.append(feature_vector(sym[:N_SYM])[0]); y.append(label); g.append(group)

    for enc in sorted(ENCODERS):
        for _ in range(PER_CLASS):
            # plaintext length chosen so the encoded stream reaches N_SYM (verbose/syllabary change length)
            plain, bid = sample_plain(int(N_SYM * {"verbose": 0.8, "syllabary": 3.2, "nomenclator": 1.6,
                                                     "abjad": 1.8}.get(enc, 1.15)))
            sym = ENCODERS[enc](plain, rng)[0]
            add(sym, enc, bid)
    for _ in range(PER_CLASS):
        plain, bid = sample_plain(int(N_SYM * 1.1))
        add([BOUNDARY if c == " " else c for c in plain], "plain", bid)
    for dec in sorted(DECOYS):
        for i in range(PER_CLASS):
            plain, bid = sample_plain(int(N_SYM * 1.2))
            src = ENCODERS["mono"](plain, rng)[0]
            sym, _ = DECOYS[dec](N_SYM + 50, rng, source_symbols=src)
            add(sym, f"decoy_{dec}", f"{dec}{i}" if dec != "markov" else bid)
    return np.array(X), np.array(y), np.array(g)


def main():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GroupKFold
    rng = random.Random(SEED)
    X, y, g = reference(rng)
    names = feature_vector(["a", "b"] * 10)[1]
    classes = sorted(set(y))
    clf = RandomForestClassifier(n_estimators=400, random_state=SEED, n_jobs=-1, min_samples_leaf=2)
    # positive control: grouped CV accuracy per class
    pred = np.empty(len(y), dtype=object)
    for tr, te in GroupKFold(5).split(X, y, g):
        clf.fit(X[tr], y[tr]); pred[te] = clf.predict(X[te])
    cv = {c: round(float(np.mean(pred[y == c] == c)), 3) for c in classes}
    confusions = {c: dict(Counter(pred[y == c]).most_common(3)) for c in classes}
    clf.fit(X, y)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    res = {"n_reference": len(y), "N_SYM": N_SYM, "classes": classes, "positive_control_cv_accuracy": cv,
           "positive_control_confusions": confusions, "voynich": {}}
    imp = sorted(zip(clf.feature_importances_, names), reverse=True)[:12]
    res["top_features"] = [[n, round(float(v), 4)] for v, n in imp]
    for fuse in (False, True):
        W = voynich_windows(fuse)
        V = np.array([feature_vector(w)[0] for w in W])
        P = clf.predict_proba(V).mean(0)
        zV = (V - mu) / sd
        typ = {}
        for c in classes:
            Zc = Z[y == c]
            cen = Zc.mean(0)
            dc = np.linalg.norm(Zc - cen, axis=1)
            dv = np.linalg.norm(zV - cen, axis=1).mean()
            typ[c] = {"voynich_dist": round(float(dv), 3), "class_dist_p95": round(float(np.percentile(dc, 95)), 3),
                      "inside_p95": bool(dv <= np.percentile(dc, 95))}
        key = "eva_multiglyph_units" if fuse else "eva_characters"
        fv = dict(zip(names, V.mean(0).round(4).tolist()))
        res["voynich"][key] = {
            "windows": len(W),
            "class_probability": dict(sorted(((c, round(float(p), 3)) for c, p in zip(clf.classes_, P)),
                                             key=lambda kv: -kv[1])),
            "typicality": typ,
            "inside_any_class_p95": [c for c, t in typ.items() if t["inside_p95"]],
            "key_features": {k: fv[k] for k in ["h1", "h_cond", "types", "ioc_x_types", "wl_mean", "word_ttr",
                                                "init_entropy", "final_entropy", "never_init_mass"]},
        }
        # same key features per reference class for context
    res["reference_key_feature_means"] = {
        c: {k: round(float(X[y == c][:, names.index(k)].mean()), 3) for k in ["h1", "h_cond", "types", "wl_mean", "word_ttr"]}
        for c in classes}
    out = ROOT / "experiments/results/e006.json"
    out.write_text(json.dumps(res, indent=1))
    print("positive control CV accuracy:", cv)
    for k, v in res["voynich"].items():
        print(k, "windows", v["windows"], "top:", list(v["class_probability"].items())[:5],
              "inside p95:", v["inside_any_class_p95"])
        print("  features:", v["key_features"])


if __name__ == "__main__":
    main()
