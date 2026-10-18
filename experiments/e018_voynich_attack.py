"""E018 (step 3): the E017 procedure, unchanged, applied to the Voynich DEV prose.

Pre-registered in reports/E018_PREREG.md. Text = Voynich DEV prose words in reading order (folio, line), unclear
tokens dropped; LOCKED_TEST leaves are excluded by e011_twin_search.voynich_lines (asserted there). Attack and claim
rule exactly as E017: attack_portfolio (128 restarts x 100k), CLAIM iff agreement >= 0.95 and lexcov7 >= 0.08.
Primary: whole DEV text x la/it/fr/de. Secondary (reported, no decision): Currier A and Currier B separately.

Run: caffeinate -ims .venv/bin/python experiments/e018_voynich_attack.py [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, hashlib, json, sys, time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e017_portfolio_known_answer as P  # noqa: E402
from vcl.solvers import verbose as V  # noqa: E402
from vcl.solvers.lm import get_lm  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

SEED = 18018
PREREG = ROOT / "reports/E018_PREREG.md"
OUT = ROOT / "experiments/results/e018.json"
G = {}


def _init(state):
    G.update(state)


def run_task(task):
    part, lm_lang, iters, restarts = task
    t0 = time.time()
    words = G["parts"][part]
    r = V.attack_portfolio(words, get_lm(lm_lang, "nospace"), iters=iters, restarts=restarts,
                           seed=SEED + P.LMS.index(lm_lang) + 10 * list(G["parts"]).index(part))
    dec = NX.clean("".join(r["decoded_words"]))
    lex = V.lexical_coverage(dec, P.vocab(lm_lang), min_len=P.LEX_LEN)
    claim = bool(r["agreement"] >= P.AGREE_MIN and lex >= P.LEX_MIN)
    return {"part": part, "lm": lm_lang, "agreement": r["agreement"], "n_agree": r["n_agree"], "lexcov7": lex,
            "claim": claim, "gap": r["gap"], "agreements_sorted": r["agreements_sorted"], "n_words": len(words),
            "n_components": r["n_components"], "n_symbols": r["n_symbols"], "n_unparsed": r["n_unparsed"],
            "decoded_preview": dec[:600], "decoded_words_first200": r["decoded_words"][:200], "key": r["key"],
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
    lines, cur, _, locked = E.voynich_lines()
    parts = {"DEV": [], "A": [], "B": []}
    for l, c in zip(lines, cur):
        ws = [w for w in l if w]
        parts["DEV"] += ws
        if c in ("A", "B"):
            parts[c] += ws
    print({k: len(v) for k, v in parts.items()}, "locked leaves excluded:", len(locked), flush=True)
    lms = P.LMS if not a.smoke else ["la"]
    tasks = [(p, lm, iters, restarts) for p in (parts if not a.smoke else ["A"]) for lm in lms]
    rows = []
    with Pool(a.workers, initializer=_init, initargs=({"parts": parts},)) as pool:
        for r in pool.imap_unordered(run_task, tasks):
            rows.append(r)
            print(f"  {r['part']:3s} lm {r['lm']} words {r['n_words']} unparsed {r['n_unparsed']} symbols "
                  f"{r['n_symbols']} agree {r['agreement']:.3f} ({r['n_agree']}) lex7 {r['lexcov7']:.3f} "
                  f"{'CLAIM' if r['claim'] else '-'} ({r['wall_s']} s)\n      {r['decoded_preview'][:110]}", flush=True)
    prim = [r for r in rows if r["part"] == "DEV"]
    claims = [r for r in prim if r["claim"]]
    pick = max(claims, key=lambda r: r["lexcov7"]) if claims else None
    res = {"experiment": "e018", "prereg": str(PREREG.relative_to(ROOT)), "prereg_sha256": prereg_sha, "seed": SEED,
           "command": " ".join(sys.argv), "iters": iters, "restarts": restarts,
           "rule": {"agree_min": P.AGREE_MIN, "lex_min": P.LEX_MIN, "lex_len": P.LEX_LEN},
           "sizes": {k: len(v) for k, v in parts.items()}, "rows": rows,
           "verdict": f"CLAIM ({pick['lm']})" if pick else "NO CLAIM",
           "secondary_claims": [(r["part"], r["lm"]) for r in rows if r["part"] != "DEV" and r["claim"]],
           "wall_s": round(time.time() - t0)}
    out = OUT if not a.smoke else ROOT / "experiments/results/smoke/e018_smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=str))
    print("verdict", res["verdict"]); print("secondary_claims", res["secondary_claims"])
    if not a.smoke:
        from vcl.eval.ledger import append
        append([dict(experiment="E018", model=f"verbose_portfolio_attack/{r['lm']}",
                     checkpoint_sha256=f"prereg={prereg_sha[:12]}", split=f"voynich_{r['part']}", metric=m,
                     value=round(v, 4), command=res["command"], notes=("CLAIM" if r["claim"] else "no claim"))
                for r in rows for m, v in (("agreement", r["agreement"]), ("lexcov7", r["lexcov7"]))])


if __name__ == "__main__":
    main()
