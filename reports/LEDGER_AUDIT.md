# E091: ledger audit (approach check 2)

Pre-registration `E091_PREREG.md` (sha256 831a8833…), script `experiments/e091_ledger_audit.py` (sha256 160b08d4…),
results `experiments/results/e091.json`, log `e091_run.log`. Run 2026-10-28.

## Findings
1. **R0, rounding drift.** Early rows were rounded and later rows continued from the rounded values. Exactly
   recomputed, the ledger before this audit was M 0.0815, L 0.8879, C 0.0241, O 0.0065 (written: 0.0887, 0.8824,
   0.0254, 0.0035).
2. **R1, two factors rested on a model later shown unlike Voynich**, and together they carried almost all of L's lead:
   - E030 L×3: "doubling languages explain Voynich's repeats". E066/E064 showed Voynich's repeats are family-level,
     unlike those languages. **Withdrawn.**
   - E036 L×10, C×3: "Indonesian + invented spellings reproduces Voynich's word features". E066 showed Indonesian
     repeats word-specifically where Voynich does not; E067/E068 showed human gibberish also makes the one-off
     richness and near-copies. **Withdrawn.**
3. **R2, double counting.** None found among same-direction factors.
4. **R3, measured ratio.** E066's pre-registered M×3 replaced by its measured ×1.4.
5. **R4, forms of L after E090.** Unattested 0.288, letter by letter (known language) 0.284, syllables 0.173, other 0.14,
   abbreviation 0.115.

## Ledger
| Rules | Point start | Start M 0.60 / L 0.15 | Start M 0.30 / L 0.45 |
|---|---|---|---|
| R0 exact (before audit) | M 0.082, L 0.888 | M 0.186, L 0.761 | M 0.038, L 0.940 |
| R1 only | M 0.649, L 0.236 | M 0.788, L 0.107 | M 0.480, L 0.392 |
| R3 only | M 0.040, L 0.928 | M 0.097, L 0.845 | M 0.018, L 0.960 |
| **All rules (new ledger)** | **M 0.4631, L 0.3604, C 0.0978, O 0.0788** | M 0.634, L 0.185 | M 0.301, L 0.527 |

**Verdict: AUDITED.** M leads from the point start and the M-high start; L leads from the L-high start. The ranking
depends on where one starts; the data so far do not decide between M and L.

## What it means
L's 0.89 rested on two early factors (×30 together) whose basis later tests overturned. The surviving factors are
small and mixed: absences of known languages (each weak after E090), the generator's failures (M×1/3), the human
gibberish results (M×3, M×1/3), the repeat behaviour (M×1.4), the verbose-cipher failure (C×1/3), same-plant pages
(M×1.4). None is a positive sign of meaning, and none is a positive sign of a specific meaningless process.
