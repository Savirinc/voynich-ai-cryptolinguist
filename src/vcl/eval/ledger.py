"""Append-only experiment ledger (experiments/LEDGER.csv)."""
from __future__ import annotations

import csv
import datetime as _dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "experiments/LEDGER.csv"
COLUMNS = ["date", "experiment", "model", "checkpoint_sha256", "split", "metric", "value", "command", "notes"]


def append(rows: list[dict], path: Path = LEDGER) -> None:
    """Append rows; create the file with header if missing. Never rewrites existing rows."""
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        for r in rows:
            r = {"date": _dt.date.today().isoformat(), **r}
            w.writerow({k: r.get(k, "") for k in COLUMNS})
