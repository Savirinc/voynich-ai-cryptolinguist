"""MLX model: Qwen2.5-0.5B (frozen, LoRA adapters) with a cipher-rank input embedding and a restricted output head.

Input side   the prompt is a left-padded window of frequency-rank ids (representation.py). Each position is embedded
             by a small trainable table `cipher_emb[id]` plus `freq_proj(log relative frequency)`; these vectors are
             fed to the transformer through `input_embeddings`, bypassing the BPE tokenizer entirely.
Output side  logits are computed only over the restricted vocabulary (plaintext characters + specials):
             characters reuse the frozen, tied Qwen token embeddings of their single-token spelling (so the pretrained
             LM's knowledge of letters/words is reused); specials (<eos>, <abstain>, family labels) are trainable rows.
             Generated tokens are fed back with the same embedding rows (tied, as in Qwen).
Trainable    LoRA (rank 16) on all attention/MLP projections of all 24 blocks + cipher_emb + freq_proj + special rows
             + output bias. Base weights (~494 M) stay frozen and are not saved; adapters are saved to checkpoints/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten, tree_unflatten

from .representation import N_IN, OUT_SPECIALS, OutVocab

BASE_MODEL = "Qwen/Qwen2.5-0.5B"
LORA_CFG = {"rank": 16, "scale": 10.0, "dropout": 0.0}


class Decipherer(nn.Module):
    def __init__(self, base, vocab: OutVocab, lora_layers: int = 24, lora_cfg: dict | None = None):
        super().__init__()
        from mlx_lm.tuner.utils import linear_to_lora_layers
        self.vocab = vocab
        base.freeze()
        linear_to_lora_layers(base, lora_layers, dict(lora_cfg or LORA_CFG))
        self.base = base
        D = base.args.hidden_size
        std = float(mx.std(base.model.embed_tokens.weight[:1000].astype(mx.float32)).item())
        self.cipher_emb = nn.Embedding(N_IN, D)
        self.cipher_emb.weight = mx.random.normal((N_IN, D), key=mx.random.key(0)) * std
        self.freq_proj = nn.Linear(1, D)
        self.freq_proj.weight = mx.zeros((D, 1))
        self.freq_proj.bias = mx.zeros((D,))
        self.special_emb = nn.Embedding(len(OUT_SPECIALS), D)
        self.special_emb.weight = mx.random.normal((len(OUT_SPECIALS), D), key=mx.random.key(1)) * std
        self.out_bias = mx.zeros((len(vocab),))
        self._char_tok = mx.array(np.array(vocab.token_ids, np.int32))

    # ------------------------------------------------------------------ embeddings
    def out_table(self) -> mx.array:
        """[V, D] embedding rows of the restricted vocabulary (frozen char rows + trainable specials)."""
        chars = mx.stop_gradient(self.base.model.embed_tokens.weight[self._char_tok])
        return mx.concatenate([chars.astype(self.special_emb.weight.dtype), self.special_emb.weight], axis=0)

    def embed_prompt(self, ids: mx.array, logf: mx.array) -> mx.array:
        return self.cipher_emb(ids) + self.freq_proj((logf / 5.0)[..., None])

    def hidden(self, emb: mx.array, cache=None) -> mx.array:
        return self.base.model(None, cache, input_embeddings=emb.astype(mx.bfloat16))

    def logits(self, h: mx.array, table: mx.array) -> mx.array:
        return (h.astype(mx.float32) @ table.T.astype(mx.float32)) + self.out_bias

    # ------------------------------------------------------------------ teacher forcing
    def __call__(self, ids, logf, out):
        """ids/logf [B,P] prompt, out [B,T] target ids. Returns logits [B,T,V] predicting out[:, t]."""
        table = self.out_table()
        prompt = self.embed_prompt(ids, logf)
        ans = table[out[:, :-1]]
        h = self.hidden(mx.concatenate([prompt, ans], axis=1))
        P = ids.shape[1]
        return self.logits(h[:, P - 1:], table)

    # ------------------------------------------------------------------ persistence
    def trainable_state(self) -> dict:
        return dict(tree_flatten(self.trainable_parameters()))

    def save(self, path: Path, meta: dict | None = None) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        mx.save_safetensors(str(path), self.trainable_state())
        (path.with_suffix(".json")).write_text(json.dumps({"vocab": self.vocab.to_json(), "base": BASE_MODEL,
                                                           "lora": LORA_CFG, **(meta or {})}, ensure_ascii=False))
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        Path(str(path) + ".sha256").write_text(f"{sha}  {path.name}\n")
        return sha

    def load_adapters(self, path: Path):
        w = mx.load(str(path))
        self.update(tree_unflatten(list(w.items())))
        mx.eval(self.parameters())


def load_base():
    from mlx_lm import load
    model, tok = load(BASE_MODEL)
    return model, tok


def build(vocab: OutVocab | None = None, adapters: Path | None = None):
    """Construct the decipherer. If `adapters` is given, the vocabulary is read from its sidecar json."""
    base, tok = load_base()
    if adapters is not None:
        meta = json.loads(Path(adapters).with_suffix(".json").read_text())
        vocab = OutVocab.from_json(meta["vocab"])
    assert vocab is not None
    m = Decipherer(base, vocab)
    if adapters is not None:
        m.load_adapters(adapters)
    return m, tok


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------- batched generation
def generate(model: Decipherer, ids: np.ndarray, logf: np.ndarray, max_new: int, temperature: float = 0.0,
             seed: int = 0, return_logprobs: bool = True):
    """Batched autoregressive decoding with a KV cache over the restricted vocabulary.

    Step 0 is constrained to a family token. A '<fam:noise>' or '<abstain>' token ends the sequence (abstain).
    Returns (tokens list[list[int]] excluding the final <eos>, sum logprob per seq, n tokens per seq,
    family-token probability distribution [B, n_fam]).
    """
    from mlx_lm.models.cache import make_prompt_cache
    V = len(model.vocab)
    voc = model.vocab
    fam_idx = sorted(voc.fam_ids.values())
    step0_mask = np.full(V, -1e9, np.float32); step0_mask[fam_idx] = 0.0
    rest_mask = np.zeros(V, np.float32); rest_mask[fam_idx] = -1e9; rest_mask[voc.unk] = -1e9
    step0_mask, rest_mask = mx.array(step0_mask), mx.array(rest_mask)
    B = ids.shape[0]
    table = model.out_table()
    cache = make_prompt_cache(model.base)
    h = model.hidden(model.embed_prompt(mx.array(ids), mx.array(logf)), cache)
    logits = model.logits(h[:, -1], table) + step0_mask
    key = mx.random.key(seed)
    toks = np.zeros((B, max_new), np.int32)
    lps = np.zeros((B, max_new), np.float32)
    done = np.zeros(B, bool)
    lengths = np.zeros(B, np.int32)
    fam_probs = None
    for t in range(max_new):
        logp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
        if temperature > 0:
            key, sub = mx.random.split(key)
            nxt = mx.random.categorical(logp / temperature, key=sub)
        else:
            nxt = mx.argmax(logp, axis=-1)
        lp = mx.take_along_axis(logp, nxt[:, None], axis=-1)[:, 0]
        if t == 0:
            fam_probs = mx.exp(logp[:, fam_idx])
        mx.eval(nxt, lp)
        n_np, lp_np = np.array(nxt), np.array(lp)
        live = ~done
        toks[live, t] = n_np[live]
        lps[live, t] = lp_np[live]
        lengths[live] += 1
        ended = (n_np == voc.eos) | (n_np == voc.abstain) | (n_np == voc.fam_ids["noise"])
        done |= ended
        if done.all():
            break
        h = model.hidden(table[nxt][:, None, :], cache)
        logits = model.logits(h[:, -1], table) + rest_mask
    fam_probs = np.array(fam_probs)
    out = []
    for i in range(B):
        seq = toks[i, : lengths[i]].tolist()
        out.append(seq)
    return out, lps, lengths, fam_probs, [voc.id_fam[j] for j in fam_idx]
