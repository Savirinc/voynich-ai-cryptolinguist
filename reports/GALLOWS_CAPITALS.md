# E106 (Arham, Reddit idea R7): are paragraph-initial gallows decorative capitals?

- **Pre-registration:** `E106_PREREG.md` (sha256 4357bc62…), commit 5838423.
- **Script:** `experiments/e106_gallows_capitals.py`. Rule 8 check: `e106b_seed_check.py`.
- **Results:** `experiments/results/e106.json`, `e106b.json`, log `e106_run.log`.

## Verdict (pre-registered): DECORATIVE, marginal. No factor
Remove the first gallows (*p, t, k, f*) of a word. Is what remains an ordinary Voynich word, used ≥ 2 times outside
paragraph starts?

| | Remainder is an ordinary word | Difference D (z) |
|---|---|---|
| **Voynich paragraph-first words** (519) | **63.2%** | |
| Voynich gallows-initial words mid-line (1,063), length-matched | 55.7% | **+0.075 (z +2.21)** |
| Generator, unplanted (10) | | −0.049 to +0.062 |
| Generator with planted decorative gallows (10) | | +0.036 to +0.121 (p10 +0.044) |

- **Validity:** VALID. Planted z > 2 in 9 of 10; unplanted |z| ≤ 2 in 8 of 10.
- **The Voynich is at the level of planted decoration:** D +0.075 ≥ +0.044.
- **Rule 8:** the z = 2 boundary was within 0.5 sd, so a seed check was run with 10 fresh bootstrap seeds. It gave z
  +2.00 to +2.32, with 9 of 10 above 2, so the verdict stands. The rule-8 step was missing from the pre-registration
  and was added as E106b before scoring; the locked script was not changed.
- **This is a marginal result.**

## Unscored observations
- **What is left is mid-line vocabulary.** The commonest remainders are *ol, chedy, chor, chol, chedar, cheol, shol,
  shedy*. Ordinary line-first words are different (*daiin, y, saiin, dain, dar, sol*). So *pchedy*, *tchor* and *pol*
  read as gallows + ordinary word.
- **By gallows:** *t* 68%, *p* 64%, *k* 54%, *f* 54%.
- **Scope:** about a third of paragraph-first words do not reduce to a known word, so not every paragraph-initial
  gallows is detachable.

## What it means
There is modest support for the Reddit idea that the paragraph-initial gallows is often an added mark (a capital or
paragraph sign) in front of an ordinary word. It fits E072, where front pieces such as *ot/ok* are detachable. Any word
statistics that treat paragraph-first words as words may count a decoration as part of the word. No factor: the idea
fits M, L and C alike.

## Ledger
No change: M 0.7422, L 0.1816, C 0.0342, O 0.0421.
