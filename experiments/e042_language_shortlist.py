"""E042 (attack step 2): the language shortlist. See reports/E042_PREREG.md.

Stage 2a, WALS (v2020.4, CLDF; files given on the command line, sha256 recorded):
  Voynich A's measured shape -> three WALS features:
    12A Syllable Structure            pass = Simple or Moderately complex      (hard filter)
    26A Prefixing vs. Suffixing       pass = Strongly or Weakly suffixing      (hard filter)
    27A Reduplication                 Productive full and partial, or Full only = "doubling language" (reported, ranks)
  (i) world base rate: share of WALS languages coded on all three that pass both hard filters, and that also double;
      families and macroareas of the full matches.
  (ii) the fixed candidate list: pass / fail / not coded on each feature. A candidate fails 2a only if a CODED hard
       feature fails; uncoded features never exclude.
Stage 2b, statistics: every candidate not failed in 2a and with a Bible text, against Voynich Currier A (cleaned, N1):
  E033's 8 spelling-independent features on non-overlapping windows of Currier A's token count (up to 10, seed 42042);
  z = (V - mean) / max(sd, 2%|V|, 0.01); fail if |z| > 3. Fails counted on all 8 and on the 7 without R (R may be a
  text-type effect, E031). SHORTLIST = candidates with <= 2 fails of 8; ranked by fails, then RMS z.
Run: caffeinate -ims .venv/bin/python experiments/e042_language_shortlist.py WALS_DIR
"""
from __future__ import annotations

import csv, hashlib, json, random, re, sys, unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
from e027_simple_syllables import bible_text  # noqa: E402
from e030_reduplication import tokens as e030_tokens  # noqa: E402
from e033_language_features import FEATS, Z_OK, feats  # noqa: E402
from e040_clean_profile import n1  # noqa: E402

SEED, KMAX = 42042, 10
OUT = ROOT / "experiments/results/e042.json"
# candidate: (WALS id or None, Bible id or None)
CANDIDATES = {
    "Latin": (None, "latVUC"), "Greek (Koine/Byzantine)": ("grk", "grcbyz"), "Hebrew": ("heb", "hboWLC"),
    "Arabic": ("aeg", "arb-vd"), "German": ("ger", "deu1912"), "Czech": ("cze", "ces1613"),
    "Polish": ("pol", "polubg"), "Hungarian": ("hun", "hun"), "Italian": ("ita", "ita1885"),
    "French": ("fre", "fraLSG"), "Occitan": (None, None), "Catalan": ("ctl", None),
    "Serbian-Croatian": ("scr", "srp1865"), "Croatian text": ("scr", "hrv"), "Slovak": (None, "slk"),
    "Slovene": ("slo", None), "Romanian": ("rom", "ron1924"), "Romani": (None, "rmc"), "Turkish": ("tur", "turytc"),
    "Armenian": ("arm", None), "Yiddish": (None, "ydd"), "Dutch": ("dut", "nld"), "English (Middle)": ("eng", "engWycliffe"),
    "Lithuanian": ("lit", "lit"), "Ukrainian/Ruthenian": ("ukr", "ukr1871"), "Albanian": ("alb", None),
    "Mandarin (Stolfi proposal; syllable tokens)": ("mnd", "cmn-cu89s"),
}
HARD_PASS = {"12A": {"12A-1", "12A-2"}, "26A": {"26A-2", "26A-3"}}
DOUBLE = {"27A-1", "27A-2"}


def words(bid):
    if bid.startswith("cmn"):
        return e030_tokens(bid)
    t = unicodedata.normalize("NFD", bible_text(bid).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")          # vowel points, accents
    t = unicodedata.normalize("NFC", t).replace("’", "'")
    return re.findall(r"[^\W\d_]+", t)


def wals(d):
    d = Path(d)
    sha = {f: hashlib.sha256((d / f).read_bytes()).hexdigest() for f in ("languages.csv", "values.csv", "codes.csv")}
    L = {r["ID"]: r for r in csv.DictReader(open(d / "languages.csv", encoding="utf-8"))}
    V = {}
    for r in csv.DictReader(open(d / "values.csv", encoding="utf-8")):
        if r["Parameter_ID"] in ("12A", "26A", "27A"):
            V.setdefault(r["Language_ID"], {})[r["Parameter_ID"]] = r["Code_ID"]
    return L, V, sha


def main():
    rng = random.Random(SEED)
    L, V, sha = wals(sys.argv[1])
    # 2a (i): world base rate
    full = {lid: v for lid, v in V.items() if len(v) == 3}
    hard = [lid for lid, v in full.items() if all(v[p] in HARD_PASS[p] for p in HARD_PASS)]
    dbl = [lid for lid in hard if full[lid]["27A"] in DOUBLE]
    base = {"coded_on_all_three": len(full), "pass_hard": len(hard), "pass_hard_share": len(hard) / len(full),
            "pass_hard_and_double": len(dbl), "pass_hard_and_double_share": len(dbl) / len(full),
            "families": Counter(L[x]["Family"] for x in dbl).most_common(),
            "macroareas": Counter(L[x]["Macroarea"] for x in dbl).most_common(),
            "languages": sorted(L[x]["Name"] for x in dbl)}
    print(f"WALS: {len(full)} languages coded on 12A+26A+27A; {len(hard)} ({base['pass_hard_share']:.0%}) pass syllables+suffixing;"
          f" {len(dbl)} ({base['pass_hard_and_double_share']:.0%}) also double", flush=True)
    print("  families:", base["families"]); print("  macroareas:", base["macroareas"]); print("  languages:", base["languages"])
    # 2a (ii): candidates
    cand = {}
    for name, (wid, bid) in CANDIDATES.items():
        v = V.get(wid, {}) if wid else {}
        status = {p: ("not coded" if p not in v else "pass" if v[p] in HARD_PASS[p] else "FAIL") for p in HARD_PASS}
        status["27A"] = "not coded" if "27A" not in v else ("doubles" if v["27A"] in DOUBLE else "no doubling")
        failed = any(status[p] == "FAIL" for p in HARD_PASS)
        cand[name] = {"wals": wid, "bible": bid, "values": v, "status": status, "fails_2a": failed}
        print(f"  2a {name:44s} 12A {status['12A']:9s} 26A {status['26A']:9s} 27A {status['27A']:11s} -> {'OUT' if failed else 'on to 2b' if bid else 'no text'}", flush=True)
    # 2b
    lines, cur, _, locked = E.voynich_lines()
    Al = [[n1(w) for w in l if w] for l, c in zip(lines, cur) if c == "A"]
    Al = [l for l in Al if l]
    nA = sum(len(l) for l in Al)
    VA = feats(Al, SEED)
    print("Voynich A (cleaned):", {k: round(float(x), 3) for k, x in VA.items()}, "tokens", nA, flush=True)
    T, shas = {}, {}
    for name, c in cand.items():
        if c["fails_2a"] or not c["bible"]:
            continue
        w = words(c["bible"])
        shas[c["bible"]] = hashlib.sha256(" ".join(w).encode()).hexdigest()
        starts = [j * nA for j in range(len(w) // nA)]
        pick = sorted(rng.sample(starts, min(KMAX, len(starts))))
        G = [feats([w[s:s + nA]], SEED + i) for i, s in enumerate(pick)]
        M = {k: float(np.mean([g[k] for g in G])) for k in FEATS}
        S = {k: max(float(np.std([g[k] for g in G], ddof=1)) if len(G) > 1 else 0.0, 0.02 * abs(VA[k]), 0.01) for k in FEATS}
        Z = {k: round((VA[k] - M[k]) / S[k], 2) for k in FEATS}
        fl = [k for k in FEATS if abs(Z[k]) > Z_OK]
        T[name] = {"bible": c["bible"], "tokens": len(w), "n_windows": len(G), "mean": M, "sd": S, "z": Z, "fail": fl,
                   "fails_no_R": [k for k in fl if k != "R"],
                   "rms": float(np.sqrt(np.mean([Z[k] ** 2 for k in FEATS]))), "wals_27A": c["status"]["27A"]}
        print(f"  2b {name:44s} n={len(G):2d} fails {len(fl)} (no R: {len(T[name]['fails_no_R'])}) " +
              " ".join(f"{k} {Z[k]:+.1f}" for k in FEATS), flush=True)
    rank = sorted(T, key=lambda n: (len(T[n]["fail"]), T[n]["rms"]))
    short = [n for n in rank if len(T[n]["fail"]) <= 2]
    verdict = "SHORTLIST" if short else "NO CANDIDATE FITS"
    print("ranking:", [(n, len(T[n]["fail"]), round(T[n]["rms"], 2)) for n in rank])
    print("VERDICT:", verdict, short)
    OUT.write_text(json.dumps({"experiment": "E042", "wals_sha256": sha, "base_rate": base, "candidates": cand,
                               "voynich_A": VA, "nA": nA, "stage2b": T, "ranking": rank, "shortlist": short,
                               "verdict": verdict, "text_sha256": shas, "locked_test_excluded": locked}, indent=1, default=str))


if __name__ == "__main__":
    main()
