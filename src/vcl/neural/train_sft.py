"""Supervised fine-tuning (SFT) of the neural decipherer.

Data: an infinite stream of freshly generated known-answer windows (vcl.neural.data.example_stream) from 'ref'-role
books of TRAIN language families, TRAIN encodings only, plus ~8% one_time_pad pure-noise windows whose target is
'<fam:noise>' (abstain). Teacher-forced cross-entropy over [family token, one output token per cipher symbol (character / space / <null>)].
A non-finite guard skips any step whose loss or gradient norm is NaN/inf (the first attempt, lr 3e-4 without the
guard, diverged to NaN between steps 250 and 300; see experiments/FAILURES.md).
Validation: teacher-forced loss / token accuracy on a fixed set of windows from 'tune'-role books (unseen documents).

Compute guard: one process, batch 8 x (257 prompt + <=258 answer) tokens, bf16 LoRA -> ~7.8 GB MLX peak on the M5;
a hard wall-clock cap (--minutes) stops training; checkpoints are written every --save-every steps.

Run: caffeinate -ims .venv/bin/python -m vcl.neural.train_sft --steps 3000 --minutes 70
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np

from . import data
from . import model as M
from .representation import build_out_vocab

ROOT = Path(__file__).resolve().parents[3]


def loss_fn(m, ids, feats, out, mask, hid, hft):
    lg = m(ids, feats, out, hid, hft)
    ce = nn.losses.cross_entropy(lg, out, reduction="none")
    ntok = mask.sum()
    acc = ((mx.argmax(lg, axis=-1) == out) * mask).sum() / ntok
    return (ce * mask).sum() / ntok, acc


def val_set(vocab, n=64, seed=999):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        t = data.gen_task(rng, "tune", p_noise=0.08, lengths=(300, 1000, 3000))
        w = data.task_windows(t, vocab)
        out.append(rng.choice(w))
    return out


def evaluate(m, vs, vocab, bs=8):
    tot, acc, n = 0.0, 0.0, 0
    for i in range(0, len(vs), bs):
        b = data.pad_batch(vs[i:i + bs], vocab.eos)
        l, a = loss_fn(m, *map(mx.array, b))
        mx.eval(l, a)
        tot += float(l); acc += float(a); n += 1
    return tot / n, acc / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=3200)
    ap.add_argument("--minutes", type=float, default=75)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--seed", type=int, default=9001)
    ap.add_argument("--p-noise", type=float, default=0.08)
    ap.add_argument("--val-every", type=int, default=250)
    ap.add_argument("--save-every", type=int, default=500)
    ap.add_argument("--out", default=str(ROOT / "checkpoints/neural_sft_v1.safetensors"))
    ap.add_argument("--log", default=str(ROOT / "experiments/results/e009_sft_log.jsonl"))
    a = ap.parse_args()
    mx.random.seed(a.seed)
    mx.set_cache_limit(1 << 30)
    t_start = time.time()
    base, tok = M.load_base()
    vocab = build_out_vocab(data.train_char_counts(), tok)
    m = M.Decipherer(base, vocab)
    mx.eval(m.parameters())
    sched = optim.join_schedules([optim.linear_schedule(1e-7, a.lr, a.warmup),
                                  optim.cosine_decay(a.lr, max(1, a.steps - a.warmup), a.lr * 0.1)], [a.warmup])
    opt = optim.AdamW(learning_rate=sched, weight_decay=0.0)
    vg = nn.value_and_grad(m, lambda *x: loss_fn(*x)[0])
    stream = data.example_stream(a.seed, "ref", vocab, p_noise=a.p_noise, max_windows_per_task=2)
    vs = val_set(vocab)
    logf = open(a.log, "w")
    meta = {"role": "sft", "args": vars(a), "n_trainable": int(sum(v.size for v in m.trainable_state().values()))}
    logf.write(json.dumps({"meta": meta}) + "\n")
    print(meta, flush=True)
    run_loss, step, tokens, skipped = None, 0, 0, 0
    fams = {}
    for step in range(1, a.steps + 1):
        ex = [next(stream) for _ in range(a.batch)]
        for e in ex:
            fams[e["family"]] = fams.get(e["family"], 0) + 1
        b = data.pad_batch(ex, vocab.eos)
        ids, mk = b[0], b[3]
        loss, g = vg(m, *map(mx.array, b))
        g, gnorm = optim.clip_grad_norm(g, 1.0)
        mx.eval(loss, gnorm)
        lv = float(loss)
        if not (np.isfinite(lv) and np.isfinite(float(gnorm))):
            skipped += 1                      # non-finite guard: never apply a NaN/inf update
            if skipped > 50:
                raise RuntimeError("too many non-finite steps")
            continue
        opt.update(m, g)
        mx.eval(m.parameters(), opt.state)
        tokens += int(mk.sum()) + ids.size
        run_loss = lv if run_loss is None else 0.98 * run_loss + 0.02 * lv
        el = time.time() - t_start
        if step % 25 == 0:
            rec = {"step": step, "loss": round(run_loss, 4), "lr": float(sched(step)), "elapsed_s": round(el, 1),
                   "tok_per_s": round(tokens / el), "skipped": skipped, "peak_gb": round(mx.get_peak_memory() / 1e9, 2)}
            if step % a.val_every == 0:
                vl, va = evaluate(m, vs, vocab)
                rec |= {"val_loss": round(vl, 4), "val_tok_acc": round(va, 4)}
            logf.write(json.dumps(rec) + "\n"); logf.flush()
            print(rec, flush=True)
        if step % a.save_every == 0:
            m.save(Path(a.out), {"step": step, "stage": "sft"})
        if el > a.minutes * 60:
            print("wall-clock cap reached", flush=True)
            break
    vl, va = evaluate(m, vs, vocab)
    sha = m.save(Path(a.out), {"step": step, "stage": "sft", "val_loss": vl, "val_tok_acc": va,
                               "train_family_windows": fams, "wall_s": round(time.time() - t_start, 1),
                               "peak_gb": round(mx.get_peak_memory() / 1e9, 2)})
    final = {"final": {"step": step, "val_loss": vl, "val_tok_acc": va, "sha256": sha, "windows_by_family": fams,
                       "wall_s": round(time.time() - t_start, 1), "peak_gb": round(mx.get_peak_memory() / 1e9, 2),
                       "size_bytes": Path(a.out).stat().st_size}}
    logf.write(json.dumps(final) + "\n"); logf.close()
    print(final, flush=True)


if __name__ == "__main__":
    main()
