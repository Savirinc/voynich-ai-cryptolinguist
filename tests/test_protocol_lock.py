import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_protocol_v1_unchanged():
    expected = (ROOT / "eval/PROTOCOL_v1.sha256").read_text().split()[0]
    actual = hashlib.sha256((ROOT / "eval/PROTOCOL_v1.md").read_bytes()).hexdigest()
    assert actual == expected, "PROTOCOL_v1.md was modified after locking; create PROTOCOL_v2.md instead"
