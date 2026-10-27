"""X085 (EXPLORATORY, unscored; Arham 2026-10-27: "no gatekeeping, show me"): best Hebrew decodes of Voynich A and B
under relaxed Hebrew forms, with no claim rule. Not a test; nothing here enters the ledger.
Hebrew model variants (hboWLC, E052 norm): full; gutturals (א ה ח ע) dropped; matres (ו י) dropped; both dropped.
Voynich: A and B as in E080, in reading order and with each line's word order reversed.
One pseudo-Voynich imitation per section is decoded with each model for reference only.
Output: experiments/results/x085.json and reports/HEBREW_EXPLORATION.md (decoded text).
Run: caffeinate -ims .venv/bin/python experiments/x085_hebrew_exploration.py [--workers 3]
"""
from __future__ import annotations

import argparse, json, random, sys, time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e047_known_answer_script as K  # noqa: E402
from e049_attack_voynich import voynich_seqs  # noqa: E402
from e050_hebrew_nearmiss import decode_task, markov_pseudo, voynich_a_by_folio  # noqa: E402
from e052_shortlist_attack import OT_LM, book_words  # noqa: E402

SEED = 85085
OUT = ROOT / "experiments/results/x085.json"
REP = ROOT / "reports/HEBREW_EXPLORATION.md"
DROP = {"full": "", "no_gutturals": "אהחע", "no_matres": "וי", "no_gutturals_no_matres": "אהחעוי"}


def reverse_lines(seqs, lens):
    out, i = [], 0
    for L in lens:
        out += list(reversed(seqs[i:i + L])); i += L
    return out + seqs[i:]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=3); a = ap.parse_args()
    t0 = time.time(); rng = random.Random(SEED)
    VA, _, _ = voynich_a_by_folio(); VB, _, _, _ = voynich_seqs("B")
    lens = [8] * (max(len(VA), len(VB)) // 8 + 1)     # reading-order chunks used only for the reversed variant
    K.LMS.clear(); tasks = []
    lm_all = book_words("hboWLC", OT_LM)
    for name, drop in DROP.items():
        ws = ["".join(c for c in w if c not in drop) for w in lm_all]
        K.LMS[name] = K.SpaceLM([w for w in ws if w], name)
        for sec, V in (("A", VA), ("B", VB)):
            for order in ("reading", "reversed"):
                seq = V if order == "reading" else reverse_lines(V, lens)
                tasks.append((f"{name}|{sec}|{order}", name, seq, None, rng.randrange(1 << 30)))
            tasks.append((f"{name}|{sec}|imitation", name, markov_pseudo(V, len(V), rng), None, rng.randrange(1 << 30)))
    with Pool(a.workers, initializer=K._init, initargs=(K.LMS,)) as pool:
        res = pool.map(decode_task, tasks)
    rows = []
    for r in res:
        name, sec, kind = r["name"].split("|")
        rows.append({"model": name, "section": sec, "kind": kind, "lexrate": r["lexrate"], "agreement": r["agreement"], "decoded": r["decoded"][:400]})
    OUT.write_text(json.dumps({"experiment": "X085 (exploratory)", "rows": rows, "runtime_s": time.time() - t0}, indent=1, ensure_ascii=False))
    lines = ["# Hebrew exploration X085 (unscored; no claim rule; Arham 2026-10-27)", "",
             "Best Hebrew decodes the attack could find. Share of decoded words of 3+ letters that are real Hebrew words of the",
             "model, and agreement between restarts. The imitation row is a meaningless Voynich-like text decoded with the same model.", "",
             "| Hebrew model | section | Voynich, reading order | Voynich, lines reversed | meaningless imitation |", "|---|---|---|---|---|"]
    get = lambda m, s, k: next(x for x in rows if x["model"] == m and x["section"] == s and x["kind"] == k)
    for m in DROP:
        for s in "AB":
            r1, r2, r3 = get(m, s, "reading"), get(m, s, "reversed"), get(m, s, "imitation")
            lines.append(f"| {m} | {s} | {r1['lexrate']:.3f} (agr {r1['agreement']:.2f}) | {r2['lexrate']:.3f} (agr {r2['agreement']:.2f}) | {r3['lexrate']:.3f} |")
    best = max((x for x in rows if x["kind"] != "imitation"), key=lambda x: x["lexrate"])
    lines += ["", f"## Highest-scoring Voynich decode: model {best['model']}, Currier {best['section']}, {best['kind']} "
              f"(lexrate {best['lexrate']:.3f})", "", "First 400 decoded words, 10 per line, in Voynich order:", "", "```"]
    d = best["decoded"]
    lines += [" ".join(d[i:i + 10]) for i in range(0, len(d), 10)] + ["```", ""]
    for m in DROP:
        r = get(m, "A", "reading")
        lines += [f"### {m}, Currier A, reading order: first 100 words", "", "```"] + [" ".join(r["decoded"][i:i + 10]) for i in range(0, 100, 10)] + ["```", ""]
    REP.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:20]), flush=True); print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
