"""E016: known-answer test -- can we crack the E014 cipher class (Naibbe inventory, SECRET letter assignment, sandhi,
nulls, ditto, merges, line-end m) from a Voynich-sized ciphertext, without being told the language?

Pre-registered in reports/E016_PREREG.md. Attack: vcl.solvers.verbose.attack (parse with the inventory, homophonic SA
under a 4-gram no-space LM, 4 restarts x 600k iterations).
  A  full size (40,000 plaintext letters ~ 27k words ~ Voynich DEV), la (3 keys) and it (5 keys) plaintext
     (role=tune books, never in the LMs; non-overlapping stretches), attacked with each of the la/it/fr/de LMs (language picked by lowest gap).
  B  quarter size (10,000 letters), true-language LM only.
  C  controls (full size, la LM): letter-shuffled la plaintext through the same cipher (3 keys); rugg_rep
     meaningless output (3 seeds). Define the confidence threshold for step 3.

Run: caffeinate -ims .venv/bin/python experiments/e016_verbose_known_answer.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, random, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

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

SEED = 16016
PREREG = ROOT / "reports/E016_PREREG.md"
OUT = ROOT / "experiments/results/e016.json"
LMS = ["la", "it", "fr", "de"]
PLAIN_LANGS = ["la", "it"]
FULL, QUARTER = 40_000, 10_000
N_KEYS = {"la": 3, "it": 5}   # non-overlapping 40k-letter stretches of role=tune text available
N_RUGG = 3
G = {}


def _init(state):
    G.update(state)


def make_cipher(kind, lang, kidx, size):
    """Deterministic ciphertext (flat word list) + labels for a task."""
    if kind == "rugg":
        p = R.random_params("rugg_rep", random.Random(1000 + kidx))
        g = R.generate("rugg_rep", p, 2000 + kidx, G["pools"], int(size / 1.5), G["C"], G["nulls"])
        return [w for l in g["lines"] for w in l], None
    text = G["texts"][lang]
    start = kidx * FULL
    text = text[start:start + size]
    if kind == "shufchar":
        r = random.Random(3000 + kidx); t = list(text); r.shuffle(t); text = "".join(t)
    key = V.random_key(SEED + 17 * kidx + (0 if lang == "la" else 1000))
    lines, labs = V.encode_labelled(text, key, G["C"], G["nulls"], seed=SEED + kidx)
    return [w for l in lines for w in l], [x for l in labs for x in l]


def run_task(task):
    tag, kind, lang, kidx, size, lm_lang, iters, restarts = task
    t0 = time.time()
    words, labels = make_cipher(kind, lang, kidx, size)
    r = V.attack(words, get_lm(lm_lang, "nospace"), iters=iters, restarts=restarts, seed=kidx)
    acc = V.char_accuracy(r["decoded_words"], labels) if labels else None
    preview = "".join(r["decoded_words"][:80])[:100]
    return {"tag": tag, "kind": kind, "plain_lang": lang, "key": kidx, "size": size, "lm": lm_lang,
            "char_acc": acc, "per_char": r["per_char"], "gap": r["gap"], "restart_per_char": r["restart_per_char"],
            "n_words": len(words), "n_components": r["n_components"], "n_symbols": r["n_symbols"],
            "n_unparsed": r["n_unparsed"], "preview": preview,
            "truth_preview": "".join(labels[:80])[:100] if labels else None, "wall_s": round(time.time() - t0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.smoke and prereg_sha is None:
        sys.exit("pre-registration missing")
    iters, restarts = (600_000, 4) if not a.smoke else (20_000, 1)
    n_keys = dict(N_KEYS) if not a.smoke else {"la": 1, "it": 1}
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
            for lm in (LMS if not a.smoke else [lg]):
                tasks.append(("A", "real", lg, k, FULL, lm, iters, restarts))
            tasks.append(("B", "real", lg, k, QUARTER, lg, iters, restarts))
    for k in range(n_keys["la"]):
        tasks.append(("C", "shufchar", "la", k, FULL, "la", iters, restarts))
    for k in range(N_RUGG if not a.smoke else 1):
        tasks.append(("C", "rugg", None, k, FULL, "la", iters, restarts))
    tasks.sort(key=lambda t: -t[4])
    print(f"{len(tasks)} attacks", flush=True)
    res_rows = []
    with Pool(a.workers, initializer=_init, initargs=(state,)) as pool:
        for r in pool.imap_unordered(run_task, tasks):
            res_rows.append(r)
            acc = f"{r['char_acc']:.3f}" if r["char_acc"] is not None else "  -  "
            print(f"  {r['tag']} {r['kind']:8s} {str(r['plain_lang']):4s} k{r['key']} n{r['size']} lm {r['lm']} "
                  f"acc {acc} gap {r['gap']:.3f} restarts {r['restart_per_char']} ({r['wall_s']} s)", flush=True)

    A = [r for r in res_rows if r["tag"] == "A"]
    cracked, lang_ok, task_rows = 0, 0, []
    for lg in PLAIN_LANGS:
        for k in range(n_keys[lg]):
            rows = [r for r in A if r["plain_lang"] == lg and r["key"] == k]
            true = next(r for r in rows if r["lm"] == lg)
            pick = min(rows, key=lambda r: r["gap"])
            cracked += true["char_acc"] >= 0.80
            lang_ok += pick["lm"] == lg
            task_rows.append({"plain_lang": lg, "key": k, "true_lm_acc": true["char_acc"], "true_lm_gap": true["gap"],
                              "picked_lm": pick["lm"], "picked_acc": pick["char_acc"],
                              "gaps": {r["lm"]: round(r["gap"], 4) for r in rows}})
    n_tasks = len(task_rows)
    ctrl = [r for r in res_rows if r["tag"] == "C"]
    ctrl_min_gap = min(r["gap"] for r in ctrl)
    succ = [t for t in task_rows if t["true_lm_acc"] >= 0.80]
    sep = sum(t["true_lm_gap"] < ctrl_min_gap for t in succ)
    B = [r for r in res_rows if r["tag"] == "B"]
    res = {"experiment": "e016", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha, "seed": SEED,
           "command": " ".join(sys.argv), "iters": iters, "restarts": restarts, "tasks": task_rows, "rows": res_rows,
           "crackable": {"n_cracked": cracked, "n": n_tasks, "verdict": "CRACKABLE" if cracked >= 0.8 * n_tasks
                         else "NOT CRACKABLE"},
           "language_id": {"n_correct": lang_ok, "n": n_tasks, "verdict": "IDENTIFIED" if lang_ok >= 0.8 * n_tasks
                           else "NOT IDENTIFIED"},
           "confidence_threshold": {"control_min_gap": ctrl_min_gap, "control_gaps": [round(r["gap"], 4) for r in ctrl],
                                    "successes_below_threshold": sep, "n_successes": len(succ)},
           "quarter_size": {"n_cracked": sum(r["char_acc"] >= 0.80 for r in B), "n": len(B),
                            "accs": [round(r["char_acc"], 3) for r in B]},
           "wall_s": round(time.time() - t0)}
    out = OUT if not a.smoke else ROOT / "experiments/results/smoke/e016_smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str))
    for k in ("crackable", "language_id", "confidence_threshold", "quarter_size"):
        print(k, json.dumps(res[k]))
    if not a.smoke:
        from vcl.eval.ledger import append
        append([dict(experiment="E016", model="verbose_homophonic_attack", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                     split="synthetic_known_answer", metric=m, value=v, command=res["command"], notes=n)
                for m, v, n in (("n_cracked_of_%d" % n_tasks, cracked, res["crackable"]["verdict"]),
                                ("language_id_correct_of_%d" % n_tasks, lang_ok, res["language_id"]["verdict"]),
                                ("control_min_gap", round(ctrl_min_gap, 4), "confidence threshold for step 3"),
                                ("quarter_size_cracked", res["quarter_size"]["n_cracked"], "10k letters"))])


if __name__ == "__main__":
    main()
