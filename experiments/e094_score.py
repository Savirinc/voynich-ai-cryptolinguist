"""E094 (Test A, Arham): score the blind zodiac judgements. See reports/E094_PREREG.md.
Reads experiments/results/e094_key.json and the judge files <JUDGE_DIR>/<COND>_j<k>.json, writes e094.json.
Run: .venv/bin/python experiments/e094_score.py JUDGE_DIR
"""
from __future__ import annotations

import json, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = ROOT / "experiments/results/e094_key.json"
OUT = ROOT / "experiments/results/e094.json"
# sign implied by the later hand's month name (its own convention: mars on the fish page, aberil on the ram pages ...)
EXPECTED = {"f70v2": "Pisces", "f70v1": "Aries", "f71r": "Aries", "f71v": "Taurus", "f72r1": "Taurus", "f72r2": "Gemini",
            "f72r3": "Cancer", "f72v3": "Leo", "f72v2": "Virgo", "f72v1": "Libra", "f73r": "Scorpio", "f73v": "Sagittarius"}
MONTH = {"f70v2": "mars", "f70v1": "aberil", "f71r": "aberil", "f71v": "may", "f72r1": "may", "f72r2": "yony", "f72r3": "iollet",
         "f72v3": "augst", "f72v2": "septembre", "f72v1": "octembre", "f73r": "novembre", "f73v": "decembre"}
LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def norm(s):
    s = (s or "").strip().lower()
    for z in SIGNS:
        if s == z.lower() or s.startswith(z.lower()):
            return z
    return "none" if "not" in s else "cannot tell"


def load(jd):
    key = json.loads(KEY.read_text())["key"]; J = {}
    for f in sorted(Path(jd).glob("*_j*.json")):
        cond, j = f.stem.rsplit("_j", 1)
        d = json.loads(f.read_text())
        J[(cond, int(j))] = {"recog": str(d.get("recognise_source", "")),
                             "pages": {key[cond][img]: v for img, v in d["images"].items() if img in key[cond]}}
    return J


def majority(votes):
    c = Counter(votes).most_common()
    if not c or (len(c) > 1 and c[0][1] == c[1][1]):
        return None, c
    return c[0][0], c


def verdict(n):
    return "ANNOTATION CONFIRMED" if n >= 10 else ("PARTLY CONFIRMED" if n >= 6 else "NOT CONFIRMED")


def main():
    J = load(sys.argv[1]); res = {"judges": {f"{c}_j{k}": v["recog"] for (c, k), v in J.items()}}
    recog = {jk for jk, v in J.items() if v["recog"].strip().lower().startswith("yes")}
    for label, excl in (("all_judges", set()), ("excluding_recognisers", recog)):
        rows, n = {}, 0
        for p, exp in EXPECTED.items():
            votes = [norm(v["pages"][p].get("zodiac_sign")) for jk, v in J.items()
                     if jk[0] in ("FULL", "CENTRE_L0") and jk not in excl and p in v["pages"]]
            m, c = majority(votes)
            ok = m == exp; n += ok
            rows[p] = {"month": MONTH[p], "expected": exp, "votes": votes, "majority": m, "match": ok}
        res[label] = {"rows": rows, "matches": n, "verdict": verdict(n) + f" ({n}/12)",
                      "judges_used": sum(1 for jk in J if jk[0] in ("FULL", "CENTRE_L0") and jk not in excl)}
        print(f"[{label}] {res[label]['verdict']}")
        for p, r in rows.items():
            print(f"  {p:6s} {r['month']:10s} expected {r['expected']:11s} votes {r['votes']} -> {r['majority']} {'MATCH' if r['match'] else 'no'}")
    deg = defaultdict(dict)
    for p, exp in EXPECTED.items():
        for L in LEVELS:
            vs = [norm(v["pages"][p].get("zodiac_sign")) for jk, v in J.items() if jk[0] == f"CENTRE_{L}" and p in v["pages"]]
            deg[p][L] = {"votes": vs, "correct": sum(x == exp for x in vs), "n": len(vs)}
    res["degradation"] = deg
    print("degradation (correct / judges):")
    for p in EXPECTED:
        print(f"  {p:6s} {EXPECTED[p]:11s} " + " ".join(f"{L}:{deg[p][L]['correct']}/{deg[p][L]['n']}" for L in LEVELS))
    feats = {}
    for p in EXPECTED:
        fj = [v["pages"][p] for jk, v in J.items() if jk[0] == "FULL" and p in v["pages"]]
        nums = [int(x["n_human_figures"]) for x in fj if str(x.get("n_human_figures", "")).strip().isdigit()]
        feats[p] = {"n_human_figures_median": statistics.median(nums) if nums else None, "n_human_figures": nums,
                    **{k: [x.get(k) for x in fj] for k in ("central_figure", "sign_reason", "rings", "figure_details",
                                                            "celestial_objects", "groupings", "astro_concept", "other")}}
    res["features"] = feats
    e73 = json.loads((ROOT / "experiments/results/e073_annotations.json").read_text())
    by = defaultdict(list)
    for r in e73:
        by[r["page"]].append(r)
    res["e073_page_features"] = {p: {"figures": len(rs), **{f: round(sum(r[f] == 1 for r in rs) / max(1, sum(r[f] != "?" for r in rs)), 2)
                                                           for f in ("BARREL", "CLOTHED", "HEAD", "HANDSTAR")}} for p, rs in by.items()}
    print("figures per page (judges' median | E073 count):", {p: (feats[p]["n_human_figures_median"], res["e073_page_features"].get(p, {}).get("figures")) for p in EXPECTED})
    res["recognisers"] = sorted(f"{c}_j{k}" for c, k in recog)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
