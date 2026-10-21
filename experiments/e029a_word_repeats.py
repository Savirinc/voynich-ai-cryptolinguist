"""E029a: key-free check of family F (and any word-for-word code) via adjacent word repeats. See reports/E029A_PREREG.md.

If each Voynich word stands for one word of the plaintext, a word written twice in a row in Voynich must be the same
plaintext word written twice in a row (distinct plaintext words cannot share a cipher word, or decoding fails).
Homophones can only remove repeats. So Voynich's adjacent-repeat rate is at most the plaintext's.
Run: caffeinate -ims .venv/bin/python experiments/e029a_word_repeats.py LATLIB_DIR
"""
from __future__ import annotations

import hashlib, json, re, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from e011_twin_search import voynich_lines, cut_blocks  # noqa: E402

MIN_WORDS = 5000
WORD = re.compile(r"[a-zà-ÿ]+")


def rate_lines(lines):
    rep = n = 0
    for l in lines:
        for a, b in zip(l, l[1:]):
            if a is None or b is None:
                continue
            n += 1; rep += a == b
    return rep / max(1, n), n


def rate_text(path):
    raw = Path(path).read_bytes()
    w = WORD.findall(raw.decode("utf-8", errors="ignore").lower())
    return sum(a == b for a, b in zip(w, w[1:])) / max(1, len(w) - 1), len(w), hashlib.sha256(raw).hexdigest()


def main():
    latlib = Path(sys.argv[1])
    lines, cur, _, locked = voynich_lines()
    V, npairs = rate_lines(lines)
    blocks = [rate_lines(b)[0] for b, _ in cut_blocks(lines, tags=cur)]
    cur_rate = {c: rate_lines([l for l, x in zip(lines, cur) if x == c])[0] for c in "AB"}

    ref = []
    for f in json.load(open(latlib / "latlib_keep.json")):
        r, n, h = rate_text(latlib / "lat_text_latin_library" / f)
        if n >= MIN_WORDS:
            ref.append({"set": "latin_library", "file": f, "words": n, "rate": r, "sha256": h})
    for p in sorted((ROOT / "data/raw/corpora/pg").glob("*.txt")):
        if p.name.split("_")[0] in ("la", "it", "fr", "de"):
            r, n, h = rate_text(p)
            if n >= MIN_WORDS:
                ref.append({"set": "pg", "file": p.name, "words": n, "rate": r, "sha256": h})
    R = np.array([x["rate"] for x in ref])
    rmax, r99, rmed = float(R.max()), float(np.percentile(R, 99)), float(np.median(R))
    b10 = float(np.percentile(blocks, 10))

    if V > rmax and b10 > r99:
        verdict = "EXCLUDED"
    elif V > r99:
        verdict = "DISFAVOURED"
    else:
        verdict = "NOT EXCLUDED"
    top = sorted(ref, key=lambda x: -x["rate"])[:10]
    out = {"experiment": "E029a", "voynich_dev": {"rate": V, "pairs": npairs, "blocks": len(blocks),
                                                 "block_p10": b10, "block_min": float(min(blocks)),
                                                 "block_max": float(max(blocks)), "currier": cur_rate},
           "reference": {"n_texts": len(ref), "median": rmed, "p99": r99, "max": rmax,
                         "n_at_or_above_voynich": int((R >= V).sum()),
                         "by_set": {s: {"n": int(sum(x["set"] == s for x in ref)),
                                        "max": max(x["rate"] for x in ref if x["set"] == s)} for s in ("latin_library", "pg")},
                         "by_lang_pg": {lg: max([x["rate"] for x in ref if x["set"] == "pg" and x["file"].startswith(lg)] or [0])
                                        for lg in ("la", "it", "fr", "de")},
                         "top10": [{k: x[k] for k in ("file", "words", "rate")} for x in top]},
           "ratio_voynich_to_median": V / rmed if rmed else None,
           "verdict": verdict, "locked_test_excluded": locked,
           "reference_files_sha256": hashlib.sha256("".join(x["sha256"] for x in ref).encode()).hexdigest()}
    (ROOT / "experiments/results/e029a.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("locked_test_excluded",)}, indent=1))


if __name__ == "__main__":
    main()
