"""Small character Transformer (decoder-only, from scratch) on the default event stream.

* Context = one manuscript line: input  [BOS] e1 ... e_{T-1}, targets e1 ... e_T
  (events as in stream.py; '_' word end, '$' line end; 28 predicted symbols).
* Optional conditioning (`cond=True`): a Currier-variety embedding (A/B/?) and a
  paragraph-first-line embedding, both added to every input position.
* Autoregressive objective only (the masked objective is not implemented; see report).
* Early stopping on an inner validation split carved from training leaves only.
* Deterministic seeds; trains on MPS when available, else CPU (MPS kernels are not
  guaranteed bit-reproducible; the checkpoint sha256 is the record of the frozen model).
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from vcl.models.stream import BOS_ID, LE_ID, V, VARIETIES, Line, decode_events, encode_line

PAD_ID = V + 1          # input-only padding id
N_IN = V + 2            # 28 symbols + BOS + PAD
IGNORE = -100


@dataclass
class TConfig:
    d_model: int = 128
    n_layers: int = 4
    n_heads: int = 4
    d_ff: int = 512
    dropout: float = 0.2
    max_len: int = 192
    cond: bool = False
    lr: float = 2e-3
    weight_decay: float = 0.1
    batch_size: int = 64
    max_epochs: int = 60
    patience: int = 6
    seed: int = 0


def default_device() -> str:
    return "mps" if torch.backends.mps.is_available() else "cpu"


class Block(nn.Module):
    def __init__(self, c: TConfig):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(c.d_model), nn.LayerNorm(c.d_model)
        self.qkv = nn.Linear(c.d_model, 3 * c.d_model)
        self.proj = nn.Linear(c.d_model, c.d_model)
        self.ff = nn.Sequential(nn.Linear(c.d_model, c.d_ff), nn.GELU(), nn.Linear(c.d_ff, c.d_model))
        self.drop = nn.Dropout(c.dropout)
        self.h, self.p = c.n_heads, c.dropout

    def forward(self, x):
        B, T, D = x.shape
        q, k, v = self.qkv(self.ln1(x)).split(D, dim=2)
        q, k, v = (t.view(B, T, self.h, D // self.h).transpose(1, 2) for t in (q, k, v))
        a = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=self.p if self.training else 0.0)
        x = x + self.drop(self.proj(a.transpose(1, 2).reshape(B, T, D)))
        return x + self.drop(self.ff(self.ln2(x)))


class CharTransformer(nn.Module):
    def __init__(self, c: TConfig):
        super().__init__()
        self.c = c
        self.tok = nn.Embedding(N_IN, c.d_model)
        self.pos = nn.Embedding(c.max_len, c.d_model)
        if c.cond:
            self.var = nn.Embedding(len(VARIETIES), c.d_model)
            self.para = nn.Embedding(2, c.d_model)
        self.drop = nn.Dropout(c.dropout)
        self.blocks = nn.ModuleList(Block(c) for _ in range(c.n_layers))
        self.ln = nn.LayerNorm(c.d_model)
        self.head = nn.Linear(c.d_model, V)
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.zeros_(m.bias)

    def forward(self, x, var=None, para=None):
        B, T = x.shape
        h = self.tok(x) + self.pos(torch.arange(T, device=x.device))[None]
        if self.c.cond:
            h = h + (self.var(var) + self.para(para))[:, None, :]
        h = self.drop(h)
        for b in self.blocks:
            h = b(h)
        return self.head(self.ln(h))       # (B, T, V) logits over predicted symbols

    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


def _batch(lines: list[Line], device):
    seqs = [encode_line(l) for l in lines]
    T = max(len(s) for s in seqs)
    x = torch.full((len(seqs), T), PAD_ID, dtype=torch.long)
    y = torch.full((len(seqs), T), IGNORE, dtype=torch.long)
    for i, s in enumerate(seqs):
        x[i, 0] = BOS_ID
        x[i, 1:len(s)] = torch.tensor(s[:-1])
        y[i, :len(s)] = torch.tensor(s)
    var = torch.tensor([VARIETIES.index(l.currier) for l in lines])
    para = torch.tensor([int(l.para_start) for l in lines])
    return x.to(device), y.to(device), var.to(device), para.to(device)


class TransformerLM:
    def __init__(self, config: TConfig | None = None, device: str | None = None, name: str | None = None):
        self.config = config or TConfig()
        self.device = device or default_device()
        torch.manual_seed(self.config.seed)
        self.net = CharTransformer(self.config).to(self.device)
        self.name = name or f"tf_d{self.config.d_model}_l{self.config.n_layers}{'+variety' if self.config.cond else ''}"
        self.history = []

    @property
    def order(self):   # for interface parity
        return self.config.max_len

    def _bits_batch(self, lines) -> torch.Tensor:
        x, y, var, para = _batch(lines, self.device)
        logits = self.net(x, var, para)
        nll = F.cross_entropy(logits.reshape(-1, V), y.reshape(-1), ignore_index=IGNORE, reduction="none")
        return nll.view(y.shape) / math.log(2), y

    def fit(self, lines: list[Line], val_lines: list[Line], log=print):
        c = self.config
        assert max(len(encode_line(l)) for l in lines) <= c.max_len
        rng = np.random.default_rng(c.seed)
        torch.manual_seed(c.seed)
        opt = torch.optim.AdamW(self.net.parameters(), lr=c.lr, weight_decay=c.weight_decay, betas=(0.9, 0.98))
        steps_per_epoch = math.ceil(len(lines) / c.batch_size)
        total = steps_per_epoch * c.max_epochs
        warm = min(200, total // 10)
        sched = torch.optim.lr_scheduler.LambdaLR(
            opt, lambda s: min(1.0, (s + 1) / warm) * 0.5 * (1 + math.cos(math.pi * min(s, total) / total)))
        best, best_state, bad = float("inf"), None, 0
        t0 = time.time()
        for ep in range(c.max_epochs):
            self.net.train()
            order = rng.permutation(len(lines))
            tr_bits = tr_n = 0.0
            for i in range(0, len(order), c.batch_size):
                bl = [lines[j] for j in order[i:i + c.batch_size]]
                b, y = self._bits_batch(bl)
                mask = y != IGNORE
                loss = b[mask].mean() * math.log(2)
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.net.parameters(), 1.0)
                opt.step()
                sched.step()
                tr_bits += float(b[mask].sum()); tr_n += int(mask.sum())
            vb = self.score(val_lines)["bits_per_glyph"]
            self.history.append({"epoch": ep, "train_bpg": tr_bits / tr_n, "val_bpg": vb, "t": time.time() - t0})
            if vb < best - 1e-4:
                best, best_state, bad = vb, copy.deepcopy(self.net.state_dict()), 0
            else:
                bad += 1
            if log and (ep % 5 == 0 or bad == 0):
                log(f"  [{self.name}] ep {ep} train {tr_bits / tr_n:.4f} val {vb:.4f} ({time.time() - t0:.0f}s)")
            if bad >= c.patience:
                break
        self.net.load_state_dict(best_state)
        self.best_val_bpg = best
        self.epochs_trained = len(self.history)
        return self

    @torch.no_grad()
    def line_bits(self, line: Line) -> np.ndarray:
        self.net.eval()
        b, y = self._bits_batch([line])
        return b[0, y[0] != IGNORE].cpu().numpy()

    @torch.no_grad()
    def score(self, lines: list[Line], bs: int = 256) -> dict:
        self.net.eval()
        bits = 0.0
        for i in range(0, len(lines), bs):
            b, y = self._bits_batch(lines[i:i + bs])
            bits += float(b[y != IGNORE].sum())
        words = sum(l.n_words for l in lines)
        events = words + sum(l.n_glyphs for l in lines)
        return {"bits": bits, "events": events, "words": words, "glyphs": events - words,
                "bits_per_glyph": bits / events, "bits_per_word": bits / words}

    @torch.no_grad()
    def sample_lines(self, conds, seed: int = 0, bs: int = 512) -> list[list[str]]:
        self.net.eval()
        g = torch.Generator(device="cpu").manual_seed(seed)
        out = []
        T = self.config.max_len
        for i in range(0, len(conds), bs):
            cc = conds[i:i + bs]
            var = torch.tensor([VARIETIES.index(v if v in VARIETIES else "?") for v, _ in cc], device=self.device)
            para = torch.tensor([int(p) for _, p in cc], device=self.device)
            x = torch.full((len(cc), 1), BOS_ID, dtype=torch.long, device=self.device)
            done = torch.zeros(len(cc), dtype=torch.bool)
            ids = []
            for _ in range(T):
                p = F.softmax(self.net(x, var, para)[:, -1].float(), -1).cpu()
                w = torch.multinomial(p, 1, generator=g)[:, 0]
                ids.append(w)
                done |= w == LE_ID
                if bool(done.all()) or x.shape[1] >= T:
                    break
                x = torch.cat([x, w[:, None].to(self.device)], 1)
            ids = torch.stack(ids, 1).tolist()
            out += [decode_events(s) for s in ids]
        return out

    def save(self, path) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {k: v.detach().cpu() for k, v in self.net.state_dict().items()}
        torch.save({"config": asdict(self.config), "name": self.name, "state_dict": state}, path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        Path(str(path) + ".sha256").write_text(f"{digest}  {path.name}\n")
        return digest

    @classmethod
    def load(cls, path, device=None):
        ck = torch.load(path, map_location="cpu")
        m = cls(TConfig(**ck["config"]), device=device, name=ck["name"])
        m.net.load_state_dict(ck["state_dict"])
        return m


def describe(model: TransformerLM) -> dict:
    return {"name": model.name, "params": model.net.n_params(), "config": asdict(model.config),
            "device": model.device}


if __name__ == "__main__":   # quick size table
    for d, l in [(64, 3), (96, 4), (128, 4), (192, 4)]:
        m = CharTransformer(TConfig(d_model=d, n_layers=l, d_ff=4 * d))
        print(d, l, m.n_params())
    print(json.dumps({"device": default_device()}))
