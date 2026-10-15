"""Encoding-family classifier with an open-set 'unknown' option, and a ciphertext-typicality score.

Trained by experiments/e003_tune.py ONLY on tasks generated from 'tune'-role books of TRAIN language families
with TRAIN encodings (mono, homophonic, vigenere, columnar, nulls). Held-out encodings/families are never seen.

  * Closed-set model: random forest over features.features() (standardised).
  * Open-set: mean distance to the k nearest training points of the predicted class in standardised feature
    space. Its empirical CDF on a held-out slice of the self-generated tune tasks gives p_unknown, which ramps
    from 0 at the 90th percentile to 1 at the 99.5th percentile of in-distribution distances.
  * typicality = 1 - p_unknown (used as a weak ciphertext-only 'looks like a train-family language cipher' cue).
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

from .features import feature_vector

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "data/derived/solver_v1"
TRAIN_ENCODINGS = ["mono", "homophonic", "vigenere", "columnar", "nulls"]


class FamilyClassifier:
    def __init__(self, k: int = 5, lo_q: float = 0.90, hi_q: float = 0.995, seed: int = 0):
        self.k, self.lo_q, self.hi_q, self.seed = k, lo_q, hi_q, seed

    def fit(self, X: np.ndarray, y: list[str], X_cal: np.ndarray, y_cal: list[str], names: list[str]):
        from sklearn.ensemble import RandomForestClassifier
        self.names = names
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        Z = (X - self.mu) / self.sd
        self.rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, random_state=self.seed, n_jobs=1)
        self.rf.fit(Z, y)
        self.classes = list(self.rf.classes_)
        self.Z = Z
        self.y = np.array(y)
        d_cal = np.array([self._dist(z, c) for z, c in zip((X_cal - self.mu) / self.sd,
                                                           self.rf.predict((X_cal - self.mu) / self.sd))])
        self.d_lo, self.d_hi = np.quantile(d_cal, self.lo_q), np.quantile(d_cal, self.hi_q)
        self.cal_acc = float(np.mean(self.rf.predict((X_cal - self.mu) / self.sd) == np.array(y_cal)))
        return self

    def _dist(self, z: np.ndarray, cls: str) -> float:
        P = self.Z[self.y == cls]
        d = np.sqrt(((P - z) ** 2).sum(1))
        return float(np.sort(d)[: self.k].mean())

    def predict(self, symbols: list[str]) -> dict:
        x, names = feature_vector(symbols)
        assert names == self.names
        z = (x - self.mu) / self.sd
        z = np.clip(z, -50, 50)
        probs = self.rf.predict_proba(z[None])[0]
        top = self.classes[int(np.argmax(probs))]
        d = self._dist(z, top)
        p_unk = float(np.clip((d - self.d_lo) / max(1e-9, self.d_hi - self.d_lo), 0, 1))
        fam_probs = {c: float(p) * (1 - p_unk) for c, p in zip(self.classes, probs)}
        fam_probs["unknown"] = p_unk
        return {"family_probs": fam_probs, "closed_probs": dict(zip(self.classes, map(float, probs))),
                "top_closed": top, "ood_distance": d, "p_unknown": p_unk, "typicality": 1 - p_unk}

    def save(self, path: Path = ART / "family_classifier.pkl"):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)


_CLF = None


def load_classifier(path: Path = ART / "family_classifier.pkl") -> FamilyClassifier:
    global _CLF
    if _CLF is None:
        with open(path, "rb") as f:
            _CLF = pickle.load(f)
    return _CLF
