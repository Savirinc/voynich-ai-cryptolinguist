"""E017: known-answer test, second attempt -- faster many-restart attack plus a two-part confidence test.

Pre-registered in reports/E017_PREREG.md. Same cipher class, plaintext stretches, sizes and control types as E016,
but FRESH secret keys and cipher seeds. Attack: vcl.solvers.verbose.attack_portfolio (128 restarts x 100k SA
iterations, delta scoring). Every text -- real or control -- is attacked with each of the la/it/fr/de no-space LMs,
except the quarter-size texts (true-language LM only).

Confidence (fixed before the run): an attack is a CLAIM if
  agreement >= 0.95   (another independent restart decodes >= 95% of components identically to the best one), and
  lexcov7  >= 0.08    (>= 8% of decoded letters covered by dictionary words of 7-14 letters from the LM's ref books).

Run: caffeinate -ims .venv/bin/python experiments/e017_portfolio_known_answer.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, random, sys, time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from vcl.solvers import verbose as V  # noqa: E402
from vcl.solvers.lm import get_lm  # noqa: E402
from vcl.synthetic import edge_twins as X  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402
from vcl.synthetic import rep_twins as R  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402

SEED = 17017
PREREG = ROOT / "reports/E017_PREREG.md"
OUT = ROOT / "experiments/results/e017.json"
LMS = ["la", "it", "fr", "de"]
PLAIN_LANGS = ["la", "it"]
FULL, QUARTER = 40_000, 10_000
N_KEYS = {"la": 3, "it": 5}
SHUF = {"la": 3, "it": 2}
N_RUGG = 3
AGREE_MIN, LEX_MIN, LEX_LEN = 0.95, 0.08, 7
G = {}
VOC = {}


def _init(state):
    G.update(state)


def vocab(lg):
    if lg not in VOC:
        VOC[lg] = {NX.clean(w) for w in get_lm(lg, "space").vocab}
    return VOC[lg]


def make_cipher(kind, lang, kidx, size):
    if kind == "rugg":
        p = R.random_params("rugg_rep", random.Random(SEED + 1000 + kidx))
        g = R.generate("rugg_rep", p, SEED + 2000 + kidx, G["pools"], int(size / 1.5), G["C"], G["nulls"])
        return [w for l in g["lines"] for w in l], None
    text = G["texts"][lang][kidx * FULL:kidx * FULL + size]
    if kind == "shufchar":
        r = random.Random(SEED + 3000 + kidx); t = list(text); r.shuffle(t); text = "".join(t)
    off = {"la": 0, "it": 1000}[lang] + (500 if kind == "shufchar" else 0)
    key = V.random_key(SEED + 17 * kidx + off)
    lines, labs = V.encode_labelled(text, key, G["C"], G["nulls"], seed=SEED + 31 * kidx + off)
    return [w for l in lines for w in l], [x for l in labs for x in l]


def run_task(task):
    tag, kind, lang, kidx, size, lm_lang, iters, restarts = task
    t0 = time.time()
    words, labels = make_cipher(kind, lang, kidx, size)
    r = V.attack_portfolio(words, get_lm(lm_lang, "nospace"), iters=iters, restarts=restarts,
                           seed=SEED + 7 * kidx + LMS.index(lm_lang))
    acc = V.char_accuracy(r["decoded_words"], labels) if labels else None
    dec = NX.clean("".join(r["decoded_words"]))
    lex = V.lexical_coverage(dec, vocab(lm_lang), min_len=LEX_LEN)
    claim = bool(r["agreement"] >= AGREE_MIN and lex >= LEX_MIN)
    return {"tag": tag, "kind": kind, "plain_lang": lang, "key": kidx, "size": size, "lm": lm_lang,
            "char_acc": acc, "agreement": r["agreement"], "n_agree": r["n_agree"], "lexcov7": lex, "claim": claim,
            "gap": r["gap"], "agreements_sorted": r["agreements_sorted"], "n_words": len(words),
            "n_components": r["n_components"], "n_symbols": r["n_symbols"], "n_unparsed": r["n_unparsed"],
            "preview": dec[:120], "truth_preview": "".join(labels)[:120] if labels else None,
            "wall_s": round(time.time() - t0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    iters, restarts = (100_000, 128) if not a.smoke else (20_000, 4)
    n_keys = dict(N_KEYS) if not a.smoke else {"la": 1, "it": 1}
    shuf = dict(SHUF) if not a.smoke else {"la": 1, "it": 0}
    n_rugg = N_RUGG if not a.smoke else 1
    lms = LMS if not a.smoke else ["la", "it"]
    lines, _, dev_words, _ = E.voynich_lines()
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    books = [b | {"role": roles.get(b["id"], {}).get("role")} for b in load_books() if b["lang"] in PLAIN_LANGS]
    texts = {}
    for lg in PLAIN_LANGS:
        ch = E.plain_chunks(books, lg, "tune", size=24000, step=24000)
        texts[lg] = NX.clean(" ".join(c[2] for c in ch))
        assert len(texts[lg]) >= N_KEYS[lg] * FULL, (lg, len(texts[lg]))
    state = {"C": X.coupling_matrix(lines), "nulls": R.null_pool(dev_words), "pools": T.chunk_pools(dev_words),
             "texts": texts}
    tasks = []
    for lg in PLAIN_LANGS:
        for k in range(n_keys[lg]):
            tasks += [("A", "real", lg, k, FULL, lm, iters, restarts) for lm in lms]
            tasks.append(("B", "real", lg, k, QUARTER, lg, iters, restarts))
        tasks += [("C", "shufchar", lg, k, FULL, lm, iters, restarts) for k in range(shuf[lg]) for lm in lms]
    tasks += [("C", "rugg", None, k, FULL, lm, iters, restarts) for k in range(n_rugg) for lm in lms]
    tasks.sort(key=lambda t: -t[4])
    print(f"{len(tasks)} attacks", flush=True)
    rows = []
    with Pool(a.workers, initializer=_init, initargs=(state,)) as pool:
        for r in pool.imap_unordered(run_task, tasks):
            rows.append(r)
            acc = f"{r['char_acc']:.3f}" if r["char_acc"] is not None else "  -  "
            print(f"  {r['tag']} {r['kind']:8s} {str(r['plain_lang']):4s} k{r['key']} n{r['size']} lm {r['lm']} "
                  f"acc {acc} agree {r['agreement']:.3f} ({r['n_agree']}) lex7 {r['lexcov7']:.3f} "
                  f"{'CLAIM' if r['claim'] else '-'} ({r['wall_s']} s)", flush=True)

    A = [r for r in rows if r["tag"] == "A"]
    texts_out, cracked, lang_ok = [], 0, 0
    for lg in PLAIN_LANGS:
        for k in range(n_keys[lg]):
            rs = [r for r in A if r["plain_lang"] == lg and r["key"] == k]
            true = next(r for r in rs if r["lm"] == lg)
            claims = [r for r in rs if r["claim"]]
            pick = max(claims, key=lambda r: r["lexcov7"]) if claims else None
            cracked += true["char_acc"] >= 0.80
            lang_ok += bool(pick and pick["lm"] == lg)
            texts_out.append({"plain_lang": lg, "key": k, "true_lm_acc": true["char_acc"], "true_lm_claim": true["claim"],
                              "picked_lm": pick["lm"] if pick else None, "claims": [r["lm"] for r in claims]})
    n = len(texts_out)
    ctrl = [r for r in rows if r["tag"] == "C"]
    false_ctrl = [r for r in ctrl if r["claim"]]
    false_wrong = [r for r in A if r["claim"] and r["char_acc"] < 0.5]
    succ = [r for r in A if r["char_acc"] >= 0.80]
    B = [r for r in rows if r["tag"] == "B"]
    res = {"experiment": "e017", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha, "seed": SEED,
           "command": " ".join(sys.argv), "iters": iters, "restarts": restarts,
           "rule": {"agree_min": AGREE_MIN, "lex_min": LEX_MIN, "lex_len": LEX_LEN}, "texts": texts_out, "rows": rows,
           "crackable": {"n_cracked": cracked, "n": n, "verdict": "CRACKABLE" if cracked >= 0.8 * n else "NOT CRACKABLE"},
           "safe": {"control_claims": len(false_ctrl), "n_controls": len(ctrl), "wrong_decode_claims": len(false_wrong),
                    "verdict": "SAFE" if not false_ctrl and not false_wrong else "NOT SAFE"},
           "language_id": {"n_correct": lang_ok, "n": n,
                           "verdict": "IDENTIFIED" if lang_ok >= 0.8 * n else "NOT IDENTIFIED"},
           "margins": {"max_control_agreement": max(r["agreement"] for r in ctrl),
                       "max_control_lexcov7": max(r["lexcov7"] for r in ctrl),
                       "min_success_agreement": min((r["agreement"] for r in succ), default=None),
                       "min_success_lexcov7": min((r["lexcov7"] for r in succ), default=None),
                       "successes_claimed": sum(r["claim"] for r in succ), "n_successes": len(succ)},
           "quarter_size": {"n_cracked": sum(r["char_acc"] >= 0.80 for r in B), "n_claimed": sum(r["claim"] for r in B),
                            "n": len(B), "accs": [round(r["char_acc"], 3) for r in B]},
           "wall_s": round(time.time() - t0)}
    res["step3"] = ("GO" if res["crackable"]["verdict"] == "CRACKABLE" and res["safe"]["verdict"] == "SAFE"
                    and res["language_id"]["verdict"] == "IDENTIFIED" else "NO GO")
    out = OUT if not a.smoke else ROOT / "experiments/results/smoke/e017_smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str))
    for k in ("crackable", "safe", "language_id", "margins", "quarter_size", "step3"):
        print(k, json.dumps(res[k]))
    if not a.smoke:
        from vcl.eval.ledger import append
        append([dict(experiment="E017", model="verbose_portfolio_attack", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                     split="synthetic_known_answer", metric=m, value=v, command=res["command"], notes=nt)
                for m, v, nt in (("n_cracked_of_%d" % n, cracked, res["crackable"]["verdict"]),
                                 ("false_claims", len(false_ctrl) + len(false_wrong), res["safe"]["verdict"]),
                                 ("language_id_correct_of_%d" % n, lang_ok, res["language_id"]["verdict"]),
                                 ("quarter_size_cracked", res["quarter_size"]["n_cracked"], "10k letters"),
                                 ("step3", 1 if res["step3"] == "GO" else 0, res["step3"]))])


if __name__ == "__main__":
    main()
