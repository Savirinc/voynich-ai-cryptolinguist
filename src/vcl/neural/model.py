"""MLX model: Qwen2.5-0.5B (frozen, LoRA adapters) with a cipher-rank input embedding and a restricted output head.

Input side   the prompt is a RIGHT-padded window of frequency-rank ids (representation.py). Each position is embedded
             by a small trainable table `cipher_emb[id]` plus `feat_proj(symbol-profile features)`; these vectors are
             fed to the transformer through `input_embeddings`, bypassing the BPE tokenizer entirely.
Answer side  answer step t receives the embedding of the previous output token PLUS the embedding of cipher symbol t
             (aligned hint), and predicts exactly one token (character / space / <null>) for that symbol. So the model
             is a tagger with autoregressive language-model context; its hypothesis class is 1:1 symbol -> token
             (with deletion), which covers all TRAIN encodings but not 1:many / many:1 mechanisms.
Output side  logits are computed only over the restricted vocabulary (plaintext characters + specials):
             characters reuse the frozen, tied Qwen token embeddings of their single-token spelling (so the pretrained
             LM's knowledge of letters/words is reused); specials (<eos>, <abstain>, family labels) are trainable rows.
             Generated tokens are fed back with the same embedding rows (tied, as in Qwen).
Trainable    LoRA (rank 16, bf16) on all attention/MLP projections of all 24 blocks + cipher_emb + feat_proj + special
             rows + output bias (~8.9 M parameters). Base weights (~494 M, bf16) stay frozen and are not saved; adapters
             are saved to checkpoints/. LoRA matrices are kept in bf16: profiling on the M5 showed fp32 LoRA promotes every
             projection's activations to fp32 (B=8 x 577 tokens peaked at 13 GB); bf16 LoRA gives 7.8 GB and 1.7x speed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten, tree_unflatten

from .representation import N_FEAT, N_IN, OUT_SPECIALS, OutVocab

BASE_MODEL = "Qwen/Qwen2.5-0.5B"
BASE_REVISION = "060db6499f32faf8b98477b0a26969ef7d8b9987"   # HF snapshot used for E009
LORA_CFG = {"rank": 16, "scale": 10.0, "dropout": 0.0}


class Decipherer(nn.Module):
    def __init__(self, base, vocab: OutVocab, lora_layers: int = 24, lora_cfg: dict | None = None):
        super().__init__()
        from mlx_lm.tuner.utils import linear_to_lora_layers
        self.vocab = vocab
        base.freeze()
        linear_to_lora_layers(base, lora_layers, dict(lora_cfg or LORA_CFG))
        for layer in base.layers:
            for _, mod in layer.named_modules():
                if hasattr(mod, "lora_a"):
                    mod.lora_a = mod.lora_a.astype(mx.bfloat16)
                    mod.lora_b = mod.lora_b.astype(mx.bfloat16)
        self.base = base
        D = base.args.hidden_size
        std = float(mx.std(base.model.embed_tokens.weight[:1000].astype(mx.float32)).item())
        self.cipher_emb = nn.Embedding(N_IN, D)
        self.cipher_emb.weight = mx.random.normal((N_IN, D), key=mx.random.key(0)) * std
        self.feat_proj = nn.Linear(N_FEAT, D)
        self.feat_proj.weight = mx.random.normal((D, N_FEAT), key=mx.random.key(2)) * (std / 4)
        self.feat_proj.bias = mx.zeros((D,))
        self.special_emb = nn.Embedding(len(OUT_SPECIALS), D)
        self.special_emb.weight = mx.random.normal((len(OUT_SPECIALS), D), key=mx.random.key(1)) * std
        self.out_bias = mx.zeros((len(vocab),))
        self._char_tok = mx.array(np.array(vocab.token_ids, np.int32))

    # ------------------------------------------------------------------ embeddings
    def out_table(self) -> mx.array:
        """[V, D] embedding rows of the restricted vocabulary (frozen char rows + trainable specials)."""
        chars = mx.stop_gradient(self.base.model.embed_tokens.weight[self._char_tok])
        return mx.concatenate([chars.astype(self.special_emb.weight.dtype), self.special_emb.weight], axis=0)

    def embed_prompt(self, ids: mx.array, feats: mx.array) -> mx.array:
        return self.cipher_emb(ids) + self.feat_proj(feats)

    def hidden(self, emb: mx.array, cache=None) -> mx.array:
        return self.base.model(None, cache, input_embeddings=emb.astype(mx.bfloat16))

    def logits(self, h: mx.array, table: mx.array) -> mx.array:
        return (h.astype(mx.float32) @ table.T.astype(mx.float32)) + self.out_bias

    # ------------------------------------------------------------------ teacher forcing
    def __call__(self, ids, feats, out, hint_ids, hint_feats):
        """Teacher forcing. ids [B,P] / feats [B,P,F] prompt, out [B,T] targets, hint_* [B,T-1] aligned cipher hints.
        Returns logits [B,T,V] predicting out[:, t]."""
        table = self.out_table()
        prompt = self.embed_prompt(ids, feats)
        ans = table[out[:, :-1]] + self.embed_prompt(hint_ids, hint_feats)
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
        (path.with_suffix(".json")).write_text(json.dumps({"vocab": self.vocab.to_json(), "base": BASE_MODEL, "base_revision": BASE_REVISION,
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
    model, tok = load(BASE_MODEL, revision=BASE_REVISION)
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
def decode_masks(vocab: OutVocab) -> tuple[np.ndarray, np.ndarray]:
    """Additive logit masks: step 0 may only emit a family token; later steps exactly one character or <null> per
    cipher symbol (no family tokens, <unk>, <eos> or <abstain>)."""
    V = len(vocab)
    fam_idx = sorted(vocab.fam_ids.values())
    step0 = np.full(V, -1e9, np.float32); step0[fam_idx] = 0.0
    rest = np.full(V, -1e9, np.float32); rest[: vocab.n_chars] = 0.0; rest[vocab.null] = 0.0
    return step0, rest


def masked_logprobs(model: Decipherer, logits: mx.array) -> mx.array:
    """Log-probabilities [B,T,V] under the same constraints that generate() samples from (used by GRPO)."""
    s0, rest = decode_masks(model.vocab)
    T = logits.shape[1]
    m = mx.concatenate([mx.array(s0)[None], mx.broadcast_to(mx.array(rest)[None], (T - 1, len(rest)))], axis=0)
    lg = logits + m[None]
    return lg - mx.logsumexp(lg, axis=-1, keepdims=True)


def generate(model: Decipherer, ids: np.ndarray, feats: np.ndarray, hint_ids: np.ndarray, hint_feats: np.ndarray,
             n_steps: np.ndarray, temperature: float = 0.0, seed: int = 0):
    """Batched aligned decoding with a KV cache over the restricted vocabulary.

    Step 0 emits a family token; '<fam:noise>' means abstain (the sequence stops). Then exactly n_steps[i] tokens
    (one per cipher symbol of window i), step t receiving the hint of cipher symbol t.
    hint_* must cover max(n_steps) positions. Returns (tokens list[list[int]] = [family] + chars,
    per-step logprobs [B, 1 + max n], family-token probabilities [B, n_fam], family names).
    """
    from mlx_lm.models.cache import make_prompt_cache
    voc = model.vocab
    fam_idx = sorted(voc.fam_ids.values())
    step0_mask, rest_mask = (mx.array(x) for x in decode_masks(voc))
    B = ids.shape[0]
    N = int(n_steps.max())
    table = model.out_table()
    cache = make_prompt_cache(model.base)
    h = model.hidden(model.embed_prompt(mx.array(ids), mx.array(feats)), cache)
    logits = model.logits(h[:, -1], table) + step0_mask
    key = mx.random.key(seed)
    toks = np.zeros((B, N + 1), np.int32)
    lps = np.zeros((B, N + 1), np.float32)
    hid, hft = mx.array(hint_ids), mx.array(hint_feats)
    fam_probs = None
    for t in range(N + 1):
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
        toks[:, t] = np.array(nxt)
        lps[:, t] = np.array(lp)
        if t == N:
            break
        if t == 0 and (toks[:, 0] == voc.fam_ids["noise"]).all():
            break
        x = table[nxt][:, None, :] + model.embed_prompt(hid[:, t:t + 1], hft[:, t:t + 1])
        h = model.hidden(x, cache)
        logits = model.logits(h[:, -1], table) + rest_mask
    out = []
    for i in range(B):
        if toks[i, 0] == voc.fam_ids["noise"]:
            out.append([int(toks[i, 0])])
        else:
            out.append(toks[i, : 1 + int(n_steps[i])].tolist())
    return out, lps, np.array(fam_probs), [voc.id_fam[j] for j in fam_idx]


def tree_map_add(a, b):
    """Elementwise sum of two gradient trees (gradient accumulation over micro-batches)."""
    from mlx.utils import tree_map
    return tree_map(lambda x, y: x + y, a, b)
