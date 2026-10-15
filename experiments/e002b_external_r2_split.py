"""E002b: APPROXIMATE comparison with the external round-2 (R2) bits/word figure (11.01).

APPROXIMATE comparison: tokenisation and scoring conventions not verified identical; their code
is not available. Sources: external/claude_chat_2026-10-15/FINAL_VERDICT.md, EXPERIMENT_LEDGER.md,
ADVERSARIAL_REPORT.md (blind leaves = 24, 33-40 (= all of quire E), 72, 80; 3,019 tokens in their
lossless corpus).

Split here:
  blind_ext = (their blind leaves) minus our LOCKED_TEST leaves (35 and 38 are in quire E and in our
              LOCKED_TEST; they are excluded, never loaded here).
  train     = all our DEV leaves (never LOCKED_TEST) minus their blind leaves.
Both sets come from `dev_lines()`, which cannot return LOCKED_TEST leaves.
Models: unigram, KN n=2..6, KN+variety (n=4), and KN conditioned on the previous word's final
glyph and on line-final position (n=3..6). Metric: bits/word on our event stream (protocol v1 s.2).

Run: .venv/bin/python experiments/e002b_external_r2_split.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.models.ngram import ConditionedKN, KneserNey, Unigram, VarietyMixKN  # noqa: E402
from vcl.models.stream import _tokens, dev_lines, inner_split, locked_set, stream_stats  # noqa: E402

LABEL = "APPROXIMATE comparison: tokenisation and scoring conventions not verified identical; their code is not available"


def main():
    toks = _tokens()
    locked = locked_set(toks)
    quire_e = sorted({t.leaf for t in toks if t.quire == "E"}, key=int)
    ext_blind = sorted(set(quire_e) | {"24", "72", "80"}, key=int)
    overlap = sorted(set(ext_blind) & locked, key=int)
    blind_used = [l for l in ext_blind if l not in locked]
    dev = dev_lines(toks)
    assert not ({l.leaf for l in dev} & locked)
    train = [l for l in dev if l.leaf not in set(ext_blind)]
    test = [l for l in dev if l.leaf in set(blind_used)]
    assert test and not ({l.leaf for l in train} & {l.leaf for l in test})
    a, b = inner_split(train)
    models = [Unigram().fit(train)] + [KneserNey(n).fit(train) for n in range(2, 7)]
    models.append(VarietyMixKN(4).fit(train, val_lines=b))
    models += [ConditionedKN(n).fit(train) for n in range(3, 7)]
    scores = {}
    for m in models:
        r = m.score(test)
        scores[m.name] = {k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()}
        print(f"{m.name:28s} {r['bits_per_glyph']:.4f} b/g  {r['bits_per_word']:.3f} b/w")
    # all-clean-prose token count of the blind set actually scored (their 3,019 counts all 11 leaves, lossless)
    prose_tokens_used = sum(1 for t in toks if t.mode == "prose" and t.leaf in set(blind_used))
    res = {
        "label": LABEL,
        "external_reference": {"blind_leaves": ext_blind, "blind_tokens_their_corpus": 3019,
                               "best_bits_per_word_blind": 11.01,
                               "best_model": "content-free char 5-gram conditioned on previous unit's final glyph "
                                             "and line-final position",
                               "dev_5fold_bits_per_word": {"plain_char_ngram": 12.00, "conditioned": 11.70,
                                                           "word_KN": 12.73}},
        "quire_E_leaves": quire_e,
        "excluded_because_in_our_LOCKED_TEST": overlap,
        "blind_leaves_scored": blind_used,
        "blind_stream": stream_stats(test) | {"prose_tokens_all_incl_unclean": prose_tokens_used},
        "train_stream": stream_stats(train),
        "scores_on_external_blind_minus_locked": scores,
        "lambda_variety": models[6].lam,
        "notes": [
            "Leaves 35 and 38 (quire E) are in our LOCKED_TEST and were not loaded; the blind set here is "
            "therefore smaller than theirs and not the same text.",
            "Our bits/word = sum of glyph bits incl. one end symbol per word ('_' or line-final '$'), clean "
            "tokens only, uncertain spaces as boundaries; their tokenisation ('lossless' ZL3b units) and exact "
            "scoring are unknown.",
            "The conditioned model is given the line-final flag of each word as side information (as described "
            "for theirs), which makes the end symbol nearly free; it is not a pure left-to-right model.",
            "These leaves are DEV leaves for us, so the hyper-parameter choices (n, model classes) were informed "
            "by DEV CV that included them (e002); not a blind result for us either.",
        ],
    }
    out = ROOT / "experiments/results/e002b.json"
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("excluded_because_in_our_LOCKED_TEST", "blind_leaves_scored", "blind_stream")}))


if __name__ == "__main__":
    main()
