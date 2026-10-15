"""Evaluation gates from eval/PROTOCOL_v1.md section 4, enforced in code.

Each gate returns {"gate": n, "status": PASS|FAIL|VOID|NOT_RUN, "reasons": [...]}. Downstream
reports must quote these objects rather than restating results by hand.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gate0_reproducibility() -> dict:
    reasons = []
    from vcl.corpus.ivtff import DOCX, DOCX_SHA256
    if _sha(DOCX) != DOCX_SHA256:
        reasons.append("IVTFF DOCX hash mismatch")
    proto = ROOT / "eval/PROTOCOL_v1.md"
    if _sha(proto) != (ROOT / "eval/PROTOCOL_v1.sha256").read_text().split()[0]:
        reasons.append("protocol modified after lock")
    bh = ROOT / "data/derived/benchmark_v1/BENCHMARK_HASHES.json"
    if bh.exists():
        for rel, h in json.loads(bh.read_text()).items():
            if _sha(bh.parent / rel) != h:
                reasons.append(f"benchmark file changed: {rel}")
    else:
        reasons.append("benchmark not built")
    if not (ROOT / "requirements.lock").exists():
        reasons.append("requirements.lock missing")
    if not (ROOT / "experiments/LEDGER.csv").exists():
        reasons.append("experiment ledger missing")
    return {"gate": 0, "status": "FAIL" if reasons else "PASS", "reasons": reasons}


def gate1_positive_control(in_family_summary: dict, families: list[str], threshold: float = 0.90) -> dict:
    """Per encoding family: mean char accuracy on matched known-answer tasks must reach threshold.
    Families that fail make any Voynich application of that solver VOID (not negative)."""
    by = in_family_summary.get("by_family", {})
    passed = {f: by.get(f, {}).get("mean_char_acc", 0.0) >= threshold for f in families}
    return {"gate": 1, "status": "PASS" if all(passed.values()) else "PARTIAL",
            "per_family": {f: {"mean_char_acc": round(by.get(f, {}).get("mean_char_acc", 0.0), 4), "pass": p}
                           for f, p in passed.items()},
            "void_families_for_voynich": [f for f, p in passed.items() if not p]}


def _binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def gate2_ood_transfer(in_summary: dict, ood_summary: dict, axis: str, chance_solved_rate: float = 0.01) -> dict:
    """Generalises iff OOD char acc >= 0.5 x in-family AND solved count beats a random-key baseline (p<0.01).
    A random key essentially never yields >= 90% char accuracy; chance_solved_rate=0.01 is conservative."""
    ind, ood = in_summary.get("mean_char_acc", 0.0), ood_summary.get("mean_char_acc", 0.0)
    n = ood_summary.get("n_language_tasks", 0)
    k = round(ood_summary.get("solved_rate", 0.0) * n)
    p = _binom_sf(k, n, chance_solved_rate) if n else 1.0
    ok = ind > 0 and ood >= 0.5 * ind and p < 0.01
    return {"gate": 2, "axis": axis, "status": "PASS" if ok else "FAIL", "in_family_char_acc": round(ind, 4),
            "ood_char_acc": round(ood, 4), "ratio": round(ood / ind, 4) if ind else None,
            "ood_solved": f"{k}/{n}", "p_vs_random_key": p}


def gate3_nonsense(null_summary: dict, max_fdr: float = 0.05) -> dict:
    fdr = null_summary.get("null_false_discovery_rate", 1.0)
    return {"gate": 3, "status": "PASS" if fdr <= max_fdr else "FAIL", "fdr": fdr,
            "by_kind": null_summary.get("null_by_kind", {})}


def gate5_semantic(evidence: dict | None = None) -> dict:
    """Semantic validation requires ALL of these, each backed by files in reports/SEMANTIC_EVIDENCE.md."""
    required = ["frozen_mapping_sha256", "original_order_readings", "independent_prediction_1",
                "independent_prediction_2", "positive_control_pass", "adversarial_reproduction"]
    evidence = evidence or {}
    missing = [r for r in required if not evidence.get(r)]
    return {"gate": 5, "status": "FAIL" if missing else "PASS", "missing": missing,
            "verdict": "no decipherment" if missing else "candidate decipherment (requires external review)"}


def freeze_environment():
    out = subprocess.run(["uv", "pip", "freeze", "--python", sys.executable], capture_output=True, text=True).stdout
    (ROOT / "requirements.lock").write_text(out)
