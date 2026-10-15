"""Combine every source's provenance into SOURCE_MANIFEST.json (handoff, IVTFF, Gutenberg corpora, external reports)."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
handoff = json.loads((ROOT / "data/raw/handoff/MANIFEST.json").read_text())
corp = json.loads((ROOT / "data/raw/corpora/SOURCE_MANIFEST.json").read_text())
ext = ROOT / "external/claude_chat_2026-10-15"
out = {
    "voynich_transliteration": {"path": "data/raw/handoff/source_dump/IVTFF Eva.txt.docx",
                                "sha256": sha(ROOT / "data/raw/handoff/source_dump/IVTFF Eva.txt.docx"),
                                "description": "ZL3b IVTFF EVA v3b 13/05/2025 (Zandbergen, EVMT)"},
    "handoff_archive": {"manifest": "data/raw/handoff/MANIFEST.json", "files": len(handoff["files"]),
                        "status": "all hashes verified by data/raw/handoff/tools/verify_manifest.py"},
    "plaintext_corpora": {"source": "Project Gutenberg", "books": len(corp["books"]),
                          "languages": sorted({b["lang"] for b in corp["books"].values()}),
                          "manifest": "data/raw/corpora/SOURCE_MANIFEST.json"},
    "external_reports": {p.name: sha(p) for p in sorted(ext.glob("*.md"))},
    "external_missing": "see reports/MISSING_EXTERNAL.md",
}
(ROOT / "SOURCE_MANIFEST.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: (v if not isinstance(v, dict) else list(v)[:4]) for k, v in out.items()}))
