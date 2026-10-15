"""E001: corpus audit, parser reproduction, locked split, and structural-effect reproduction.

Run: .venv/bin/python experiments/e001_corpus_audit.py
Writes data/derived/tokens.csv, data/derived/splits.json, experiments/results/e001.json.
"""
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus.ivtff import parse, legacy064_tokens, token_dicts, DOCX_SHA256  # noqa: E402
from vcl.corpus.splits import locked_test_leaves, dev_folds, SALT  # noqa: E402
from vcl.corpus.effects import effect_report  # noqa: E402


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    pages, toks = parse()
    locked = locked_test_leaves(toks)
    folds = dev_folds(toks)
    derived = ROOT / "data/derived"; derived.mkdir(parents=True, exist_ok=True)
    rows = token_dicts(toks)
    with open(derived / "tokens.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) + ["split"])
        w.writeheader()
        for r in rows:
            r["split"] = "LOCKED_TEST" if r["leaf"] in locked else f"dev{folds[r['leaf']]}"
            w.writerow(r)
    (derived / "splits.json").write_text(json.dumps({"salt": SALT, "locked_test_leaves": locked,
                                                    "dev_folds": folds}, indent=1))
    legacy = legacy064_tokens()
    lp = [x for x in legacy if x["mode"] == "prose"]
    prose = [t for t in toks if t.mode == "prose"]
    res = {
        "source_docx_sha256": DOCX_SHA256,
        "pages": len(pages), "all_tokens": len(toks), "tokens_by_mode": Counter(t.mode for t in toks),
        "prose": {"tokens": len(prose), "clean": sum(t.is_clean for t in prose),
                  "uncertain_glyph": sum(t.uncertain_glyph for t in prose),
                  "alternative_reading": sum(t.alternative for t in prose),
                  "ligature_braces": sum(t.ligature for t in prose),
                  "rare_glyph": sum(t.rare_glyph for t in prose),
                  "single_glyph_words": sum(len(t.eva) == 1 for t in prose),
                  "uncertain_space_before": sum(t.space_before == "," for t in prose)},
        "leaves": len({t.leaf for t in toks}), "bifolios": len({t.bifolio_id for t in toks}),
        "locked_test_leaves": locked, "locked_test_prose_tokens": sum(t.leaf in locked for t in prose),
        "legacy064_reproduction": {"prose_tokens": len(lp), "prose_types": len({x['word'] for x in lp}),
                                   "label_tokens": sum(x["mode"] == "label" for x in legacy),
                                   "prose_folios": len({x['folio'] for x in lp}),
                                   "prose_leaves": len({x['leaf'] for x in lp}),
                                   "currier_A": sum(x["variety"] == "A" for x in lp),
                                   "currier_B": sum(x["variety"] == "B" for x in lp),
                                   "targets": {"prose_tokens": 32132, "prose_types": 6846, "label_tokens": 875,
                                               "prose_folios": 206, "prose_leaves": 99,
                                               "currier_A": 9878, "currier_B": 21760}},
        # effects computed on DEV leaves only: locked leaves stay untouched
        "effects_dev_only": effect_report(toks, folds, exclude_leaves=locked),
        "effects_by_currier_dev_only": {
            v: effect_report([t for t in toks if t.currier == v], folds, exclude_leaves=locked)
            for v in ("A", "B")},
        "derived_hashes": {"tokens.csv": sha(derived / "tokens.csv"), "splits.json": sha(derived / "splits.json")},
    }
    rp = res["legacy064_reproduction"]
    res["legacy064_reproduction"]["exact_match"] = all(rp[k] == v for k, v in rp["targets"].items())
    out = ROOT / "experiments/results/e001.json"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=dict))
    print(json.dumps({k: res[k] for k in ["prose", "leaves", "bifolios", "locked_test_prose_tokens"]}, default=dict))
    print("legacy064 exact match:", rp["exact_match"])
    for k, v in res["effects_dev_only"].items():
        print(k, json.dumps(v))
    for c, r in res["effects_by_currier_dev_only"].items():
        print("Currier", c, "y->q OR", r["y_to_q"]["odds_ratio"], r["y_to_q"]["ci95_leaf_bootstrap"],
              "| m OR", r["line_final_m_vs_iin"]["odds_ratio"], r["line_final_m_vs_iin"]["ci95_leaf_bootstrap"])
    print("locked leaves:", locked)


if __name__ == "__main__":
    main()
