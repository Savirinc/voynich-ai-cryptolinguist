# E093: the simplest writing process, and do the free choices follow the pictures? (approach check 4)

Pre-registration `E093_PREREG.md` (sha256 7d72b6bc…), script `experiments/e093_explanation_model.py` (sha256 d1db7f3e…),
results `experiments/results/e093.json`, log `e093_run.log`. Run 2026-10-28, 43 s.

**Counting correction:** the prereg says "13 items"; the list it gives has 12 (B1, B2, six B3, B4, B5, B6, B7). The
verdict rule ("all items") is unaffected.

## Part 1: process ladder: NO WORKING PROCESS
Held-out bits per word: P1 13.19, P2 13.10, P3 13.40, P4 13.04 → P\* = P4 (copy probability 0.2, alternation 0.3, last
100 words). Reproduced items (>= 4 of 5 samples):
| Item | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| word length (WL), ending concentration (END5), family-level repeats (E066), content partners (E070), lines independent | yes | yes | yes | yes |
| book vocabulary, vocabulary at 150, word-length spread, H2, back-to-back repeats R, near-copies NR, common-word partners (E069) | no | no | no | no |
P4 reproduces 5 of 12. The samples are poor Voynich ("chs qey okm"): the glyph chain for middles makes too many odd
words, and even with copying at 0.2 the back-to-back repeat rate is not reached. Junction rules (P3) made held-out
prediction worse than P2 (over-fitting).

**Reading:** this ladder does not explain the text, so no M factor. Its failures are partly the models' weakness, not
proof that no meaningless process can; the facts it misses (rigid word shapes with rich vocabulary, Voynich's repeat and
near-copy rates, weak but real common-word partners) are the ones no process, meaningful or not, has yet reproduced.

## Part 2: subject tracking: INCONCLUSIVE
| Text | Pairs | DELTA | Permutation z | Rule |
|---|---|---|---|---|
| Vulgate (genre) | 14,365 | +0.0147 | **+16.0** | known answer, >= 3 ✓ |
| KJV (genre) | 14,706 | +0.0216 | **+14.3** | known answer, >= 3 ✓ |
| Generator with Voynich labels | 4,650 | −0.0073 | −2.4 | false-claim control, < 2 ✓ |
| P\* sample with Voynich labels | 4,650 | −0.0085 | −5.0 | false-claim control, < 2 ✓ |
| **Voynich** | 4,650 | **+0.0058** | **+1.2** | 1 <= z < 3: INCONCLUSIVE |
VALID; Voynich INCONCLUSIVE; no factor. Ledger unchanged.

**Unscored observation (not pre-registered, read with care):** both meaningless controls come out clearly *negative*
with Voynich's page labels (−0.007, −0.009), probably because the label layout pairs pages of very different sizes
(the permutation null ignores page size). Voynich is +0.006. Measured against the controls instead of the permutation
null, Voynich's pages of the same subject share about 0.014 more vocabulary than meaningless text laid out the same way,
which is roughly 3 control-sd. This is the closest thing to a sign of meaning the programme has seen, but the
comparison was chosen after seeing the result. It needs its own pre-registered test with a size-matched null.
