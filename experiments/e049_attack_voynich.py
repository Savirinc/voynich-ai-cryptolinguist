"""E049 (attack step 3b): the E047-validated attack on Voynich itself. See reports/E049_PREREG.md.
Voynich Currier A (primary) and Currier B (secondary): DEV prose only (LOCKED_TEST excluded), cleaned (N1), cut into
S3 units, the 23 commonest Voynich-A signs kept as cipher symbols (rarer units dropped, count recorded), word spaces
kept. Attack and LMs exactly as E047 (Hebrew, Turkish, Latin; 32 restarts x 30,000 steps). Controls in the same run:
2 sign-shuffled copies of Voynich A and 2 fresh copy-generator samples, each against all three LMs.
CLAIM = agreement >= 0.95 and lexrate >= 0.514 (E047 DEV threshold) and lexrate >= (max control lexrate in this run)
+ 0.10.
Run: caffeinate -ims .venv/bin/python experiments/e049_attack_voynich.py
"""
from __future__ import annotations

import json, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e024_atoms as A24  # noqa: E402
import e047_known_answer_script as K  # noqa: E402
from e040_clean_profile import n1  # noqa: E402

SEED = 49049
OUT = ROOT / "experiments/results/e049.json"
T_LEX, AGREE, MARGIN = 0.514, 0.95, 0.10


def voynich_seqs(currier):
    signs, _ = K.voynich_signs(); idx = {s: i + 1 for i, s in enumerate(signs)}
    lines, cur, _, locked = E.voynich_lines()
    out, dropped, total = [], 0, 0
    for l, c in zip(lines, cur):
        if c != currier:
            continue
        for w in l:
            if not w:
                continue
            us = A24.segment(n1(w), A24.SEGS["S3"]); total += len(us)
            u = [idx[x] for x in us if x in idx]; dropped += len(us) - len(u)
            if u:
                out.append(u)
    return out, dropped, total, locked


def main():
    rng = random.Random(SEED)
    for l in K.LANGS:
        K.LMS[l] = K.SpaceLM(K.book_words(l, K.LM_BOOKS), l)
    VA, dA, tA, locked = voynich_seqs("A"); VB, dB, tB, _ = voynich_seqs("B")
    print(f"Voynich A: {len(VA)} words, {dA}/{tA} rare units dropped; B: {len(VB)} words, {dB}/{tB} dropped", flush=True)
    tasks = []
    for lml in K.LANGS:
        tasks.append(("VOYNICH_A", lml, VA, None, rng.randrange(1 << 30)))
        tasks.append(("VOYNICH_B", lml, VB, None, rng.randrange(1 << 30)))
    for k in range(2):
        sh = K.shuffled(VA, rng)
        g = K.gibberish_streams(len(VA), rng)
        for lml in K.LANGS:
            tasks.append((f"CONTROL:shuffledA{k}", lml, sh, None, rng.randrange(1 << 30)))
            tasks.append((f"CONTROL:generator{k}", lml, g, None, rng.randrange(1 << 30)))
    with Pool(3, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(K.attack, tasks)
    ctrl = [r for r in res if r["name"].startswith("CONTROL")]
    cmax = max(r["lexrate"] for r in ctrl)
    ctrl_claims = [r for r in ctrl if r["agreement"] >= AGREE and r["lexrate"] >= T_LEX]
    for r in res:
        r["claim"] = (not r["name"].startswith("CONTROL")) and r["agreement"] >= AGREE and r["lexrate"] >= T_LEX and r["lexrate"] >= cmax + MARGIN
        print(f"{r['name']:22s} {r['lm']} agreement {r['agreement']:.3f} lexrate {r['lexrate']:.3f} claim {r['claim']}", flush=True)
    a_claims = [r["lm"] for r in res if r["name"] == "VOYNICH_A" and r["claim"]]
    if ctrl_claims:
        verdict = "VOID (a control reached the claim bar)"
    elif len(a_claims) == 1:
        verdict = f"CLAIM: Voynich A reads as {a_claims[0]} (needs LOCKED_TEST confirmation, E050)"
    elif len(a_claims) > 1:
        verdict = "AMBIGUOUS (claims under several languages): treated as no claim"
    else:
        verdict = "NO CLAIM"
    print(f"max control lexrate {cmax:.3f}; VERDICT: {verdict}")
    OUT.write_text(json.dumps({"experiment": "E049", "results": res, "max_control_lexrate": cmax, "verdict": verdict,
                               "units_dropped": {"A": [dA, tA], "B": [dB, tB]}, "locked_test_excluded": locked},
                              indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
