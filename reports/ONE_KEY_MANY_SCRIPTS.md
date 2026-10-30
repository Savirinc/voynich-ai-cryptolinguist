# E097 (Arham): one key for the whole book, signs borrowed from several period scripts, zodiac anchor

Pre-registration `E097_PREREG.md` (sha256 f89476a2…), script `experiments/e097_one_key.py` (sha256 71d93e75…).
Results `experiments/results/e097.json`, log `e097_run.log`. Run 2026-10-29/30, 57,013 s wall clock (laptop slept
overnight; about 2.5 h of computing per worker).

## Verdict: VALID, NO CLAIM. L × 0.943 (L-alpha-known share × 0.8)

## The design (Arham)
- One key for every scribe and both Currier A and B (the common words run through all five hands).
- The signs may borrow sounds from several scripts: 10 period languages of the region (Latin, Italian, Occitan,
  Catalan, French, German, Czech, Greek, Hebrew, Arabic) in one 30-sound alphabet, with each line free to be in any
  of them, plus 10 shorthand values (us, um, is, er, ur, rum, kon, per, pro, kwe).
- Anchor: the zodiac pages are not meaningless. Starting keys come from exact matches of 6 training zodiac pages to
  their own sign's material (8 languages + period star names).
- Fit on half the book (2,122 lines); judge on the other half (2,419 lines) and on 6 zodiac pages the fit never saw.
- Claim needs: real-word share (types) on the held-out half ≥ the DEV threshold (0.306) AND held-out zodiac pages
  matched with a new own-sign word beyond the 720 sign permutations (p ≤ 0.05).

## Known answers first
| Book | Held-out real words (types) | Held-out zodiac pages | p | Key accuracy | Claimed |
|---|---|---|---|---|---|
| D1 Latin | 0.484 | 6/6 | 0.001 | 1.00 | yes |
| D2 Catalan + Latin | 0.600 | 6/6 | 0.001 | 1.00 | yes |
| T1 Italian + Hebrew | 0.137 | 5/6 | 0.001 | 0.71 | no (search trap) |
| T2 Czech + German + Latin | 0.480 | 6/6 | 0.001 | 1.00 | yes |
| T3 Greek + Arabic + Latin | 0.331 | 3/6 | 0.008 | 0.92 | yes |
| T4 Occitan + Catalan | 0.501 | 6/6 | 0.001 | 0.99 | yes |

Controls (meaningless): generator ×2, shuffled Voynich ×2, shuffled T1, generator with the zodiac anchor planted:
real-word share 0.085–0.132, zodiac 0–1 of 6 (p 0.33–1.0). **0 false claims.** TEST cracks claimed 3 of 4 (needed
≥ 3). Validation passed.

## Voynich
| Measure | Voynich | Needed | Meaningless controls |
|---|---|---|---|
| Held-out real words (types) | **0.131** | ≥ 0.306 | 0.085–0.132 |
| Held-out zodiac pages with a new own-sign word | **0 of 6** (p 1.0) | p ≤ 0.05 | 0–1 of 6 |
| Agreement between the two best fits | 0.15 | — | 0.16–0.99 |
| Language chosen per line | Hebrew 2,217, Arabic 178, Occitan 8 | — | shuffled texts: Hebrew ~2,080 |

- The best Voynich fit came from the free start, not from a zodiac anchor: the anchored keys did not fit the rest of
  the book as well.
- The key gives almost no vowels (o→w, a→j, e→l, y→h), so nearly every line is read as Hebrew/Arabic, which are
  written without vowels and so accept consonant strings. The shuffled-Voynich controls do the same.
- Fitted key: o w, k q, ch k, y h, a j, l n, e l, d b, r t, iin m, sh q, qo b, s m, ckh S, dy h, m m, p S, in m,
  i d, ir r, f x, cph p, h r.

## What it means
- Under one key, with signs borrowed from any of the 10 regional languages line by line and shorthand allowed, the
  Voynich reads no better than shuffled Voynich, and the key that fits the training zodiac pages finds nothing on the
  zodiac pages it did not see.
- The attack could find this kind of writing: it cracked 5 of 6 synthetic books, including two- and three-language
  mixtures, and made no false claims.
- Not excluded: languages outside the 10; keys with more than 23 signs or other sign cuts; spelling not by sound;
  readings of the zodiac that are not own-sign words.

## Ledger
NO CLAIM (validated): the searched sub-form within L-alpha-known × 0.8, so L × 0.943.
M 0.4728, L 0.3469, C 0.0998, O 0.0804. Forms of L: unattested 0.305, alpha-known 0.241, syll 0.183, other 0.148,
abbrev 0.122.
