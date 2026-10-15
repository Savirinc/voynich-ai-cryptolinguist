"""Deterministic physical-leaf splits.

* LOCKED_TEST: ~15% of leaves, stratified by illustration section, chosen by a salted
  SHA-256 rank. These leaves are excluded from all model development and are scored
  exactly once per frozen model (Gate 4). The salt and resulting leaf list are written
  into eval/PROTOCOL_v1.md before any model is trained.
* DEV folds: remaining leaves into K folds by salted hash rank (GroupKFold-like).
Grouping by bifolio (physical sheet) is available as a stricter alternative.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict

SALT = "vcl-protocol-v1-2026-10-15"
LOCKED_FRACTION = 0.15


def _rank(key: str) -> str:
    return hashlib.sha256(f"{SALT}:{key}".encode()).hexdigest()


def leaf_sections(tokens) -> dict[str, str]:
    """Section of a leaf = illustration type of its lowest-numbered page in the corpus."""
    sec = {}
    for t in tokens:
        sec.setdefault(t.leaf, t.illustration)
    return sec


def locked_test_leaves(tokens) -> list[str]:
    by_sec = defaultdict(list)
    for leaf, sec in leaf_sections(tokens).items():
        by_sec[sec].append(leaf)
    locked = []
    for sec, leaves in sorted(by_sec.items()):
        leaves.sort(key=_rank)
        k = max(1, round(LOCKED_FRACTION * len(leaves))) if len(leaves) >= 4 else 0
        locked += leaves[:k]
    return sorted(locked, key=lambda x: (len(x), x))


def dev_folds(tokens, k: int = 5) -> dict[str, int]:
    locked = set(locked_test_leaves(tokens))
    leaves = sorted({t.leaf for t in tokens} - locked, key=_rank)
    return {leaf: i % k for i, leaf in enumerate(leaves)}
