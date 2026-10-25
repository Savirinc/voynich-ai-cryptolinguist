# E062 (campaign step 2): a verbose cipher with one table per scribe — CLASS FAILS (C × 1/3)

Pre-registration `reports/E062_PREREG.md` (sha256 f78106ff…564b, commit 26d0544). Script
`experiments/e062_scribe_tables.py` (sha256 7d75494d…f492). Results: `experiments/results/e062.json`, `e062_run.log`.
80 twins (4 plaintexts × 10 seeds × 2 variants), 144 s. Sanity check passed: decoding each sample with its own
scribe's tables recovers 98.8–99.7% of the plaintext characters.

## Verdict (pre-registered rule): CLASS FAILS. Best per-scribe set (German) fails 8 of 13 features; Latin 9, Hebrew 10,
Turkish 11. Every language fails at least 5. **C × 1/3.**

## What the per-scribe tables fixed, and what they did not
German plaintext; "fail" is |z| > 3. z is Voynich's distance from the twin set in standard deviations.

| Feature | Voynich | One table for all (E013-style) | z | **One table per scribe** | z |
|---|---|---|---|---|---|
| common words persist (PERS_30) | 0.26 | 0.73 | −28.5 | 0.35 | −1.9 pass |
| common words cover the text (COV_30) | 0.92 | 1.00 | −4.5 | 0.93 | −0.4 pass |
| Zipf slope | −0.65 | −0.75 | +7.7 | −0.59 | −2.5 pass |
| glyph predictability (h2) | 2.10 | 2.08 | +0.5 | 2.22 | −2.9 pass |
| ending marking (DIST) | 0.37 | 0.36 | +0.6 | 0.33 | +2.1 pass |
| **repeats, same word next to itself (R)** | **2.65** | 0.62 | +37 | 0.94 | **+24** |
| near-copies next to each other (NR) | 2.11 | 0.91 | +24 | 1.03 | **+18** |
| word length | 4.99 | 5.56 | −5.7 | 5.87 | **−8.8** |
| distinct words | 6,077 | 5,593 | +4.0 | 7,580 | **−12.4** |
| words seen once | 0.68 | 0.52 | +11.7 | 0.58 | **+7.3** |
| topic clustering (I_word) | 0.39 | 0.006 | +38 | 0.24 | **+8.6** |
| concentrated types (top_word) | 0.29 | 0.003 | +28 | 0.18 | **+6.0** |
| endings covering 95% (NSUF95) | 29 | 39 | −3.1 | 55 | **−6.1** |

## Plain reading
1. **Giving each scribe his own table does what E020 hoped:** the common words stop being spread evenly through the
   book (persistence and coverage now match), and the Zipf head flattens to Voynich's value. Section-wise key change
   was the right idea for those three facts.
2. **It cannot touch the repeats.** Voynich puts the same word next to itself 2.6× chance; this cipher 0.9×, the single
   table 0.6×. A letter-level cipher only repeats a word when the plaintext repeats a letter pair under the same
   card draw, which is rare. This is C9/C21 again, the fact that has sunk every letter cipher since E016, now including
   the per-scribe form.
3. **It overshoots the vocabulary.** Five table sets make 7,580 distinct words where Voynich has 6,077, yet fewer of
   them are one-offs (58% vs 68%). More keys give more forms, not more rare forms. Voynich's rarity is of a different
   kind: a long tail of forms that occur once, inside a vocabulary of ordinary size.
4. **Topic clustering is still only two-thirds of Voynich's** (0.24 vs 0.39): key changes by scribe mimic section
   vocabulary, but Voynich's words also cluster within a scribe's own pages (E059: by sheet).
5. **Taken with E061:** stems behave like a language's stems, not a code alphabet (E061), and a letter-level cipher
   with changing tables cannot produce the repeats or the rare-word tail (E062). The surviving space for C is now a
   **word-level** system over a doubling plaintext, or a mixed system with deliberate repetition, both of which are
   already heavily constrained (X3 for la/it/fr/de).

## Ledger
C × 1/3: C 0.0274 → 0.0093. M 0.0078, L 0.9815, O 0.0013 after renormalisation. Sensitivity: from the range edges
(L 0.60, M 0.25, C 0.13, O 0.02) the update gives C 0.052, L 0.70, M 0.29. **The ranking does not change inside the
ranges.** C's honest range is now about 0.01–0.05.

## Observation recorded (not a test): the two key-like pages
The f57v ring (17 signs × 4) and the f66r margin column (34 single signs) share a sign set that the running text barely
uses: four rare signs that occur nowhere else, x (18 times in 28,841 words) and v (once), while omitting a, e, i,
ch/sh, n, q and s, the commonest glyphs of the text. Whatever these pages are, they are not an alphabet of the running
text. Either they list a plaintext alphabet in another notation, or they are marginal play with a wider repertoire.
The planned E064 periodicity test is dropped as misdirected.
