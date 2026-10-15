"""Build the frozen known-answer benchmark (configs/benchmark_v1.yaml).

Output (data/derived/benchmark_v1/):
  public/<split>.jsonl   PublicTask rows  - the only thing solvers/agents may read
  secret/<split>.jsonl   SecretAnswer rows - evaluator only
  book_roles.json        which Gutenberg books are reference/tune/test (public)
  BENCHMARK_HASHES.json  SHA-256 of every file
Every encoded task is round-trip verified against its exact decoder before being written.

Run: .venv/bin/python -m vcl.synthetic.benchmark
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import yaml

from .corpora import load_books, ROOT
from .decoys import DECOYS
from .encoders import ENCODERS, decode, comparable
from .schema import PublicTask, SecretAnswer, save_jsonl, BOUNDARY

CONFIG = ROOT / "configs/benchmark_v1.yaml"
OUT = ROOT / "data/derived/benchmark_v1"


def book_roles(books, cycle):
    by_lang = {}
    for b in books:
        by_lang.setdefault(b["lang"], []).append(b)
    roles = {}
    for lang, bs in by_lang.items():
        bs.sort(key=lambda b: hashlib.sha256(f"roles:{b['id']}".encode()).hexdigest())
        for i, b in enumerate(bs):
            roles[b["id"]] = cycle[i % len(cycle)]
    return roles


def sample_plaintext(text, length, rng):
    start = rng.randrange(0, max(1, len(text) - length - 50))
    sp = text.find(" ", start)
    chunk = text[sp + 1: sp + 1 + length]
    return chunk[: chunk.rfind(" ")] if " " in chunk else chunk


def make_task(tid, split, fam, book, length, seed):
    rng = random.Random(seed)
    plain = sample_plaintext(book["text"], length, rng)
    if fam == "short_mono":
        syms, key, ident, recov = ENCODERS["mono"](plain, rng); fam_enc = "mono"
        ident = "non_identifiable"
    else:
        syms, key, ident, recov = ENCODERS[fam](plain, rng); fam_enc = fam
    dec = decode(fam_enc, syms, key) if key is not None else None
    if dec is not None and comparable(fam_enc, dec) != comparable(fam_enc, recov):
        raise AssertionError(f"round-trip failed for {fam} task {tid}")
    sec = SecretAnswer(task_id=tid, is_language=True, plaintext=plain, family=fam, key=key,
                       language=book["lang"], language_family=book["family"], source_id=book["id"],
                       source_url=book["url"], seed=seed,
                       difficulty={"plaintext_chars": len(plain), "symbols": len(syms),
                                   "glyph_types": len(set(syms) - {BOUNDARY})},
                       identifiability=ident, recoverable_plaintext=recov)
    return PublicTask(tid, syms, split), sec


def build():
    cfg = yaml.safe_load(CONFIG.read_text())
    books = load_books()
    roles = book_roles(books, cfg["book_role_cycle"])
    for b in books:
        b["role"] = roles[b["id"]]
    rng = random.Random(cfg["seed"])
    trainF, heldF = set(cfg["train_language_families"]), set(cfg["heldout_language_families"])
    trainE, heldE = cfg["train_encodings"], cfg["heldout_encodings"]

    def pool(families, role):
        return [b for b in books if b["family"] in families and b["role"] == role]

    plan = {
        "tune": (pool(trainF, "tune"), trainE),
        "test_in": (pool(trainF, "test"), trainE),
        "test_lang": (pool(heldF, "test"), trainE),
        "test_enc": (pool(trainF, "test"), heldE),
        "test_both": (pool(heldF, "test"), heldE),
    }
    publics, secrets = {}, {}
    for split, (bks, fams) in plan.items():
        if not bks:
            raise RuntimeError(f"no books for split {split}")
        P, S = [], []
        # stratify: cycle over languages so small languages are represented
        langs = sorted({b["lang"] for b in bks})
        for i in range(cfg["tasks_per_split"][split]):
            lang = langs[i % len(langs)]
            book = rng.choice([b for b in bks if b["lang"] == lang])
            fam = fams[(i // len(langs)) % len(fams)] if len(langs) > 1 else fams[i % len(fams)]
            fam = rng.choice(fams) if i % 3 == 2 else fam
            length = rng.choice(cfg["plaintext_lengths"])
            p, s = make_task(f"{split}-{i:04d}", split, fam, book, length, rng.randrange(2**31))
            P.append(p); S.append(s)
        publics[split], secrets[split] = P, S

    # nulls: decoys + non-identifiable controls
    P, S = [], []
    real_streams = [p.symbols for p in publics["test_in"]]
    n = cfg["tasks_per_split"]["test_null"]
    test_books = pool(trainF | heldF, "test")
    for i in range(n):
        tid, seed = f"test_null-{i:04d}", rng.randrange(2**31)
        r = random.Random(seed)
        kind = (cfg["decoys"] + cfg["non_identifiable"])[i % (len(cfg["decoys"]) + len(cfg["non_identifiable"]))]
        if kind in DECOYS:
            length = r.choice([400, 1200, 3500])
            src = r.choice(real_streams)
            syms, meta = DECOYS[kind](length, r, source_symbols=src)
            P.append(PublicTask(tid, syms, "test_null"))
            S.append(SecretAnswer(task_id=tid, is_language=False, plaintext=None, family=kind, key=meta,
                                  language=None, language_family=None, source_id=None, source_url=None, seed=seed,
                                  difficulty={"symbols": len(syms)}, identifiability="non_identifiable"))
        else:
            length = cfg["short_mono_length"] if kind == "short_mono" else r.choice([300, 1000])
            p, s = make_task(tid, "test_null", kind, r.choice(test_books), length, seed)
            P.append(p); S.append(s)
    publics["test_null"], secrets["test_null"] = P, S

    hashes = {}
    for split in publics:
        for kind, rows in (("public", publics[split]), ("secret", secrets[split])):
            path = OUT / kind / f"{split}.jsonl"
            save_jsonl(path, rows)
            hashes[f"{kind}/{split}.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "book_roles.json").write_text(json.dumps(
        {b["id"]: {"lang": b["lang"], "family": b["family"], "role": b["role"]} for b in books}, indent=1))
    hashes["book_roles.json"] = hashlib.sha256((OUT / "book_roles.json").read_bytes()).hexdigest()
    (OUT / "BENCHMARK_HASHES.json").write_text(json.dumps(hashes, indent=1))
    for split, rows in secrets.items():
        fams = sorted({r.family for r in rows}); langs = sorted({r.language or '-' for r in rows})
        print(f"{split:10s} n={len(rows):4d} families={fams} languages={langs}")
    return hashes


if __name__ == "__main__":
    build()
