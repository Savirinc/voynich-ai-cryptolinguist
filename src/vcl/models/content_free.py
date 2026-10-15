"""Content-free generator baseline and posterior predictive checks P1-P6 (PROTOCOL_v1 section 2).

The generator is ancestral sampling from a frozen structure model (KN n-gram or char
Transformer). It knows nothing but glyph-sequence statistics: no meaning, no language, no
plaintext. If it reproduces a structural effect, that effect is explainable by local
sequence statistics alone; this says nothing about content.

Checks (thresholds fixed by the protocol):
  P1 y->q odds ratio of samples within the leaf-bootstrap 95% CI of the held-out data.
  P2 line-final m/iin odds ratio within the held-out CI.
  P3 q->o share within +-0.02 of held-out.
  P4 variety-conditioned model reproduces the sign of the A/B difference for P1 and P2.
  P5 label ot/ok/op/of-initial share >= 0.55 (absolute threshold on the samples).
  P6 type/token ratio of samples within +-10% of held-out at matched length.
Statistics use the effects.py implementations on Token-like sample objects.
"""
from __future__ import annotations

from dataclasses import dataclass

from vcl.corpus.effects import bootstrap_ci, lines_of, m_table, pooled_or, qo_share, yq_table

LABEL_PREFIXES = ("ot", "ok", "op", "of")


@dataclass
class SampleToken:
    eva: str
    leaf: str
    folio: str
    line_no: int
    currier: str = "?"
    mode: str = "prose"
    is_clean: bool = True


def to_tokens(word_lines, curriers, lines_per_leaf: int = 40) -> list[SampleToken]:
    """Wrap sampled lines as Token-like objects. Pseudo-leaves of `lines_per_leaf` lines allow
    a cluster bootstrap on samples comparable to the leaf bootstrap on data."""
    out = []
    for i, (ws, cur) in enumerate(zip(word_lines, curriers)):
        leaf = f"S{i // lines_per_leaf}"
        out += [SampleToken(w, leaf, leaf, i, cur) for w in ws]
    return out


def ttr(words, n: int) -> float:
    ws = list(words)[:n]
    return len(set(ws)) / len(ws)


def structure_stats(tokens, with_ci: bool = True, seed: int = 0) -> dict:
    """y->q OR, m/iin OR, q->o share, with leaf-bootstrap CIs (2000 resamples)."""
    lines = lines_of(tokens)
    out = {}
    for name, fn in [("y_to_q", yq_table), ("line_final_m_vs_iin", m_table)]:
        per = fn(lines)
        or_, tab = pooled_or(per)
        out[name] = {"odds_ratio": or_, "table": tab}
        if with_ci and len(per) > 1:
            out[name]["ci95"] = list(bootstrap_ci(per, seed=seed))
    qo, q = qo_share(lines)
    out["q_to_o"] = {"qo": qo, "q": q, "share": qo / q if q else float("nan")}
    return out


def label_share(words) -> float:
    ws = list(words)
    return sum(w.startswith(LABEL_PREFIXES) for w in ws) / max(len(ws), 1)


def reference_stats(prose_tokens, label_tokens, stream_words, by_variety: dict | None = None) -> dict:
    """Held-out reference statistics. prose_tokens: real Token objects of the reference leaves;
    stream_words: words of the default stream in reading order (for TTR)."""
    ref = structure_stats(prose_tokens)
    ref["n_words"] = len(stream_words)
    ref["ttr"] = ttr(stream_words, len(stream_words))
    ref["words"] = list(stream_words)
    ref["label_share_data"] = label_share(t.eva for t in label_tokens if t.is_clean)
    if by_variety:
        ref["by_variety"] = {v: structure_stats(toks, with_ci=False) for v, toks in by_variety.items()}
    return ref


def sample_stats(word_lines, curriers) -> dict:
    toks = to_tokens(word_lines, curriers)
    st = structure_stats(toks)
    words = [t.eva for t in toks]
    st["n_words"] = len(words)
    st["words"] = words
    st["label_share_all_words"] = label_share(words)
    st["label_share_line_initial"] = label_share(ws[0] for ws in word_lines if ws)
    st["by_variety"] = {}
    for v in ("A", "B"):
        idx = [i for i, c in enumerate(curriers) if c == v]
        st["by_variety"][v] = structure_stats(to_tokens([word_lines[i] for i in idx], [v] * len(idx)), with_ci=False)
    return st


def run_checks(samp: dict, ref: dict, cond_samp: dict | None = None) -> dict:
    """Apply P1-P6 exactly per protocol thresholds. `cond_samp` = stats of samples from the
    variety-conditioned model (for P4); defaults to `samp`."""
    cond_samp = cond_samp or samp
    res = {}
    for key, name in [("P1_y_to_q_OR", "y_to_q"), ("P2_line_final_m_vs_iin_OR", "line_final_m_vs_iin")]:
        lo, hi = ref[name]["ci95"]
        v = samp[name]["odds_ratio"]
        res[key] = {"sample": v, "sample_ci95_pseudoleaf": samp[name].get("ci95"), "heldout": ref[name]["odds_ratio"],
                    "heldout_ci95": [lo, hi], "pass": bool(lo <= v <= hi)}
    s, h = samp["q_to_o"]["share"], ref["q_to_o"]["share"]
    res["P3_q_to_o_share"] = {"sample": s, "heldout": h, "tolerance": 0.02, "pass": bool(abs(s - h) <= 0.02)}
    p4 = {}
    if "by_variety" in ref and ref["by_variety"]:
        ok = True
        for name in ("y_to_q", "line_final_m_vs_iin"):
            d_ref = ref["by_variety"]["B"][name]["odds_ratio"] - ref["by_variety"]["A"][name]["odds_ratio"]
            d_s = cond_samp["by_variety"]["B"][name]["odds_ratio"] - cond_samp["by_variety"]["A"][name]["odds_ratio"]
            same = (d_ref > 0) == (d_s > 0) and d_s != 0
            ok &= same
            p4[name] = {"heldout_A": ref["by_variety"]["A"][name]["odds_ratio"],
                        "heldout_B": ref["by_variety"]["B"][name]["odds_ratio"],
                        "sample_A": cond_samp["by_variety"]["A"][name]["odds_ratio"],
                        "sample_B": cond_samp["by_variety"]["B"][name]["odds_ratio"], "sign_match": bool(same)}
        p4["pass"] = bool(ok)
    else:
        p4["pass"] = None
    res["P4_currier_AB_sign"] = p4
    res["P5_label_initial_share"] = {"sample_all_words": samp["label_share_all_words"],
                                     "sample_line_initial": samp["label_share_line_initial"],
                                     "data_label_share_reference_only": ref.get("label_share_data"),
                                     "threshold": 0.55, "pass": bool(samp["label_share_all_words"] >= 0.55)}
    n = min(ref["n_words"], samp["n_words"])
    t_s = ttr(samp["words"], n)
    t_h = ttr(ref["words"], n)
    res["P6_type_token_ratio"] = {"matched_n": n, "sample": t_s, "heldout": t_h, "rel_diff": (t_s - t_h) / t_h,
                                  "tolerance": 0.10, "pass": bool(abs(t_s - t_h) / t_h <= 0.10)}
    res["n_pass"] = sum(bool(v.get("pass")) for v in res.values() if isinstance(v, dict))
    return res
