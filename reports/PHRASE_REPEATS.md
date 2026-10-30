# E099 (Arham, Reddit idea R3): does the Voynich reuse multi-word phrases?

- **Pre-registration:** `E099_PREREG.md` (sha256 3332a9ed…).
- **Amendment:** `E099_AMENDMENT.md`, an indentation fix before any run.
- **Script:** `experiments/e099_phrase_repeats_v2.py`.
- **Results:** `experiments/results/e099.json`, log `e099_run.log`. Run 2026-10-30, 154 s.

## Verdict (pre-registered rule): PHRASES LIKE LANGUAGE, M × 1/3. Fragile: see the caveat.

## Known answers
| Group | Q3 (repeated 3-word sequences ÷ shuffle) | Raw repeated 3-word tokens | Repeated 4-word tokens |
|---|---|---|---|
| 69 meaningful texts | p10 6.50, min 3.63 (Ilocano), median 19.6 | 344–11,502 (median 3,697) | 60–5,316 (median 1,114) |
| Copy generator (10) | 2.0–4.75 | 112–502 (median 307) | 0–59 (median 9) |
| **Voynich** | **11.9** (236 vs 18.9 ± 5.0 by shuffle) | **236** | **0** |

VALID (p10 6.50 > generator max 4.75). The Voynich is 1.8 shuffle-sd above the p10 boundary, so no seed check was
needed.

## Caveat (unscored, seen after the run)
- **Raw counts point the other way.** The Voynich's raw count of repeated 3-word sequences (236) is below every
  meaningful text (minimum 344) and inside the generator's range (112–502). Its Q3 is high because, with its very rich
  vocabulary (6,077 types against the generator's about 3,800), shuffling almost never repeats a 3-word sequence by
  chance (18.9).
- **Q depends on richness.** As the shuffle count approaches zero, Q approaches the raw count, so a richer text gets
  a higher Q from the same reuse. The pre-registered ratio therefore favours the Voynich in a way the known answers
  could not reveal: no control matched its vocabulary richness.
- **The Reddit claim holds.** The Voynich has no repeated 4-word or 5-word sequence at all inside lines. Every
  meaningful text has at least 60; the generator has 0–59.
- **Some triples may be spacing artefacts.** Among the commonest repeated triples are *ol s aiin* (5 times) and
  *l s aiin* (3), which may come from uncertain spaces (*s aiin* ~ *saiin*; E092).

**Assessment:** the factor stands as pre-registered, but its basis is fragile. A follow-up with a control matched in
vocabulary richness should decide whether it is kept.

## Ledger
M × 1/3: M 0.2424, L 0.5336, C 0.1003, O 0.1237.
