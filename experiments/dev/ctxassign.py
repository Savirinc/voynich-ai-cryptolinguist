"""Probe 10: context assignment. Given key m, each symbol's score for candidate stem L given its CURRENT neighbours:
G[s, L] = sum_p Cprev[s,p] log P(L | m(p)) + sum_n Cnext[s,n] log P(m(n) | L); then solve one injective assignment
on G + wu*U for all symbols at once (Hungarian), iterate, keep if the total improves; SA polish between rounds."""
import numpy as np, scipy.sparse as sp_
from scipy.optimize import linear_sum_assignment

def ctx_round(m, seq, S, K, lm, U, wu, damp=1.0):
    a, b = seq[:-1], seq[1:]
    keep = (a < S) | (b < S)
    Cp = sp_.coo_matrix((np.ones(keep.sum()), (b[keep], a[keep])), shape=(S + 1, S + 1)).tocsr()   # row = symbol, col = prev
    Cn = sp_.coo_matrix((np.ones(keep.sum()), (a[keep], b[keep])), shape=(S + 1, S + 1)).tocsr()   # row = symbol, col = next
    LP = np.asarray(lm.logp, dtype=np.float64)
    G = Cp @ LP[m][:, 1:K] + Cn @ LP[1:K][:, m].T       # (S+1, K-1): candidate L = 1..K-1
    W = damp * G[1:S] + wu * U[1:S]
    r, c = linear_sum_assignment(-W)
    m2 = m.copy(); m2[1 + r] = c + 1
    return m2
