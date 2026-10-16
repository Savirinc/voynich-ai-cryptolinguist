"""GRPO (group-relative policy optimisation) from verifiable rewards, starting from the SFT adapters.

This is genuine on-policy RL: each step samples G outputs per prompt from the CURRENT policy (temperature 1.0, same
constrained decoding as inference), scores them with a verifiable reward computed from our OWN copy of the scoring
logic on self-generated known answers (vcl.neural.reward.window_reward: char accuracy vs the known plaintext, +1 for
abstaining on one_time_pad noise, penalties for confident-wrong and degenerate output, small bonus for the right
family token), and takes a policy-gradient step with group-normalised advantages

    A_i = (r_i - mean_g r) / (std_g r + 1e-4),    loss = - sum_i A_i * sum_t log pi(o_i,t | ...) / (G * WINDOW)

(one update per batch, so the PPO ratio is 1 and clipping is inactive; LoRA kept in fp32 during RL, lr 5e-6; a constant length normaliser as in Dr.GRPO
avoids the length bias of per-sequence means). No KL term (beta = 0) and no reference model: memory/time budget;
the small constant learning rate keeps the policy near SFT. Prompts: windows of fresh tasks from 'ref'-role books,
TRAIN families x TRAIN encodings + 10% noise; no decoy generator, no test data.

We did not use mlx-lm-lora's GRPO trainer: it expects tokenised text prompts and the stock LM head, whereas this model
takes rank/feature embeddings as input and decodes over a restricted vocabulary.

Run: caffeinate -ims .venv/bin/python -m vcl.neural.train_grpo --sft checkpoints/neural_sft_v1.safetensors --minutes 35
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
from .representation import WINDOW
from .reward import char_acc, window_reward

ROOT = Path(__file__).resolve().parents[3]


def pg_loss(m, ids, feats, out, mask, hid, hft, adv):
    lg = m(ids, feats, out, hid, hft)
    lp = M.masked_logprobs(m, lg)
    tok = mx.take_along_axis(lp, out[..., None], axis=-1)[..., 0]
    return -((tok * mask).sum(axis=1) * adv).sum()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sft", default=str(ROOT / "checkpoints/neural_sft_v1.safetensors"))
    ap.add_argument("--out", default=str(ROOT / "checkpoints/neural_grpo_v1.safetensors"))
    ap.add_argument("--log", default=str(ROOT / "experiments/results/e009_grpo_log.jsonl"))
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--minutes", type=float, default=45)
    ap.add_argument("--prompts", type=int, default=4)
    ap.add_argument("--group", type=int, default=6)
    ap.add_argument("--micro", type=int, default=4)
    ap.add_argument("--lr", type=float, default=5e-6)
    ap.add_argument("--bf16-lora", action="store_true", help="keep LoRA in bf16 (attempt 1; updates got rounded)")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--p-noise", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=9101)
    a = ap.parse_args()
    t0 = time.time()
    mx.random.seed(a.seed)
    mx.set_cache_limit(1 << 30)
    m, _ = M.build(adapters=Path(a.sft))
    if not a.bf16_lora:
        # fp32 master copy of the LoRA matrices: RL-sized updates (~lr) are below half a bf16 ulp of the SFT
        # weights and would be rounded away / applied inconsistently (GRPO attempt 1 degraded the policy).
        for layer in m.base.layers:
            for _, mod in layer.named_modules():
                if hasattr(mod, "lora_a"):
                    mod.lora_a = mod.lora_a.astype(mx.float32)
                    mod.lora_b = mod.lora_b.astype(mx.float32)
        mx.eval(m.parameters())
    vocab = m.vocab
    opt = optim.AdamW(learning_rate=a.lr, weight_decay=0.0)
    vg = nn.value_and_grad(m, pg_loss)
    rng = random.Random(a.seed)
    logf = open(a.log, "w")
    logf.write(json.dumps({"meta": {"role": "grpo", "args": vars(a), "kl_beta": 0.0}}) + "\n")
    hist = []
    step = 0
    for step in range(1, a.steps + 1):
        prompts = []
        for _ in range(a.prompts):
            task = data.gen_task(rng, "ref", p_noise=a.p_noise, lengths=(300, 1000, 3000))
            w = rng.choice(data.task_windows(task, vocab))
            prompts.append(w | {"family": task["family"]})
        G = a.group
        ids = np.stack([p["ids"] for p in prompts for _ in range(G)])
        ft = np.stack([p["feats"] for p in prompts for _ in range(G)])
        n_steps = np.array([p["b"] - p["a"] for p in prompts for _ in range(G)])
        hid, hft = data.pad_hints([p for p in prompts for _ in range(G)], int(n_steps.max()))
        toks, _, _, _ = M.generate(m, ids, ft, hid, hft, n_steps, temperature=a.temperature, seed=a.seed + step)
        rewards, cas, abst = [], [], []
        for k, seq in enumerate(toks):
            p = prompts[k // G]
            fam = vocab.id_fam.get(seq[0]) if seq else None
            ab = fam == "noise"
            txt = None if ab else vocab.decode([x for x in seq[1:] if x < vocab.n_chars])
            rewards.append(window_reward(txt, fam, p["target_text"], p["family"]))
            abst.append(ab)
            if p["target_text"] is not None:
                cas.append(char_acc(txt, p["target_text"]))
        r = np.array(rewards, np.float32).reshape(a.prompts, G)
        adv = ((r - r.mean(1, keepdims=True)) / (r.std(1, keepdims=True) + 1e-4)).reshape(-1)
        adv = adv / (G * a.prompts * WINDOW)
        T = max(2, max(len(s) for s in toks))
        out = np.full((len(toks), T), vocab.eos, np.int32)
        mask = np.zeros((len(toks), T), np.float32)
        for k, s in enumerate(toks):
            out[k, :len(s)] = s; mask[k, :len(s)] = 1.0
        thid, thft = data.pad_hints([p for p in prompts for _ in range(G)], T - 1)
        live = np.nonzero(np.abs(adv) > 0)[0]
        grads = None
        for i in range(0, len(live), a.micro):
            sl = live[i:i + a.micro]
            loss, g = vg(m, mx.array(ids[sl]), mx.array(ft[sl]), mx.array(out[sl]), mx.array(mask[sl]),
                         mx.array(thid[sl]), mx.array(thft[sl]), mx.array(adv[sl]))
            grads = g if grads is None else M.tree_map_add(grads, g)
            mx.eval(grads)
        if grads is not None:
            grads, gn = optim.clip_grad_norm(grads, 1.0)
            mx.eval(gn)
            if np.isfinite(float(gn)):
                opt.update(m, grads)
                mx.eval(m.parameters(), opt.state)
        rec = {"step": step, "reward": float(r.mean()), "char_acc": float(np.mean(cas)) if cas else None,
               "abstain_rate": float(np.mean(abst)), "group_std": float(r.std(1).mean()),
               "elapsed_s": round(time.time() - t0, 1), "peak_gb": round(mx.get_peak_memory() / 1e9, 2)}
        hist.append(rec)
        logf.write(json.dumps(rec) + "\n"); logf.flush()
        if step % 10 == 0:
            last = hist[-10:]
            print({"step": step, "reward10": round(float(np.mean([h["reward"] for h in last])), 4),
                   "char_acc10": round(float(np.mean([h["char_acc"] for h in last if h["char_acc"] is not None])), 4),
                   "elapsed": rec["elapsed_s"], "peak_gb": rec["peak_gb"]}, flush=True)
        if step % 50 == 0:
            m.save(Path(a.out), {"step": step, "stage": "grpo", "sft": a.sft})
        if time.time() - t0 > a.minutes * 60:
            print("wall-clock cap reached", flush=True)
            break
    sha = m.save(Path(a.out), {"step": step, "stage": "grpo", "sft": a.sft, "wall_s": round(time.time() - t0, 1)})
    final = {"final": {"step": step, "sha256": sha, "wall_s": round(time.time() - t0, 1),
                       "peak_gb": round(mx.get_peak_memory() / 1e9, 2), "size_bytes": Path(a.out).stat().st_size,
                       "reward_first50": float(np.mean([h["reward"] for h in hist[:50]])),
                       "reward_last50": float(np.mean([h["reward"] for h in hist[-50:]]))}}
    logf.write(json.dumps(final) + "\n"); logf.close()
    print(final, flush=True)


if __name__ == "__main__":
    main()
