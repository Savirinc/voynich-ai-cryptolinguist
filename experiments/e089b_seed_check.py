"""E089b: rule-8 seed check of E089's near-threshold result (Hebrew + Aramaic + Judeo-Arabic, Voynich B, COVER5 0.172 vs
threshold 0.175). Voynich B is decoded with 10 further seeds; each seed is judged by E089's fixed rule (COVER5 >= T,
> B-control maximum, agreement >= 0.95), with T and the B-control maximum taken from experiments/results/e089.json.
CLAIM stands only if >= 8 of 10 seeds pass. See reports/E089B_PREREG.md.
Run: caffeinate -ims .venv/bin/python experiments/e089b_seed_check.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, sys, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
import e087_spaceless_attack_v3 as S  # noqa: E402
import e089_spaceless_mixtures as E  # noqa: E402
from e088_spaceless_hebrew_family import cover_min  # noqa: E402
from e050_hebrew_nearmiss import decode_task  # noqa: E402

NAME, SEEDS = "heb+aram+jarab", [89101 + i for i in range(10)]
OUT = ROOT / "experiments/results/e089b.json"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time()
    prev = json.load(open(ROOT / "experiments/results/e089.json"))["mixtures"][NAME]
    T, cB = prev["threshold"], prev["controls_max_B"]
    V, _, _ = S.voynich_lines_units()
    w = E.stream(NAME); cut = int(len(w) * 0.6); lmw = w[:cut]
    chunks = ["".join(lmw[i:i + 10]) for i in range(0, len(lmw), 10)]
    K.LMS.clear(); K.LMS[NAME] = K.SpaceLM(chunks, NAME); letters = set(K.LMS[NAME].letters)
    mw = [x for x in ("".join(ch for ch in y if ch in letters) for y in lmw) if x]
    vocab = {x for x, c in Counter(mw).items() if c >= 2 and len(x) >= 3}
    tasks = [(f"{NAME}:VOYNICH_B:seed{s}", NAME, V["B"], None, s) for s in SEEDS]
    with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    rows = []
    for r in res:
        sc = cover_min(r["decoded"], vocab, 5)
        ok = sc >= T and sc > cB and r["agreement"] >= K.AGREE_MIN
        rows.append({"seed": r["name"].split("seed")[1], "cover5": sc, "agreement": r["agreement"], "pass": ok})
        print(f"seed {rows[-1]['seed']}: COVER5 {sc:.3f} agreement {r['agreement']:.2f} {'PASS' if ok else 'fail'}", flush=True)
    n = sum(x["pass"] for x in rows)
    verdict = "CLAIM STANDS (>= 8/10)" if n >= 8 else ("NO CLAIM (<= 2/10 pass)" if n <= 2 else "UNSTABLE (3-7/10): no claim")
    print(f"threshold {T:.4f}, B controls max {cB:.4f}; {n}/10 seeds pass -> {verdict} | {time.time() - t0:.0f}s", flush=True)
    OUT.write_text(json.dumps({"experiment": "E089b", "threshold": T, "controls_max_B": cB, "seeds": rows, "passes": n, "verdict": verdict}, indent=1))


if __name__ == "__main__":
    main()
