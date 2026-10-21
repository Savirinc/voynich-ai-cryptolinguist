# E032 (ledger test 3): the authors' own copy-and-change generator — FAILS on 7 of 13 features

Pre-registration: `reports/E032_PREREG.md` (sha256 623d8c55…9722, locked before the run). Script
`experiments/e032_copy_generator.py`. Generator: Timm & Schinner, github.com/TorstenTimm/SelfCitationTextgenerator
@ a6ede22 (MIT), shipped settings, seeds 1–10, no tuning by us. Results: `experiments/results/e032.json`,
`e032_run.log`.

## Plain-language result
The generator gets the *local* texture of Voynich right but not the *vocabulary*.

**It reproduces six features:**
- exact copies of neighbouring words;
- near-copies;
- glyph predictability inside words;
- topic clustering;
- the number of endings and how they are written.

That is real: a meaningless copying process can produce the habits we found in E030 and E031.

**It fails on seven features, all about the vocabulary as a whole:**

| Feature | Voynich | Generator (mean ± sd) | z |
|---|---|---|---|
| distinct words | 6,077 | 3,961 ± 156 | +13.6 |
| share of words seen once | 0.68 | 0.52 | +11.4 |
| Zipf slope | −0.65 | −0.82 | +4.6 |
| common words persist (PERS_30) | 0.26 | 0.56 | −6.7 |
| common words cover the text (COV_30) | 0.92 | 0.98 | −3.0 |
| concentrated word types (top_word) | 0.29 | 0.49 | −5.4 |
| word length | 4.99 | 4.63 | +3.3 |

Matched (|z| ≤ 3): R +1.5, NR −0.7, h2 +1.6, I_word −0.8, NSUF95 +1.8, DIST +0.4.

So Voynich has **more, rarer words** than the copying process makes. Its common words are also **less evenly spread**
through the book: they come and go more, the way content words do in a real text that changes subject. The
generator's text is a uniform soup.

By the pre-registered rule (5 or more fails): **AUTHORS' GENERATOR FAILS**, so **M × 1/3**.

## Caveats
- **Only weak evidence against M, by design.** A human writer is more flexible than this program, and the authors
  say so. Other settings (more mutation, a "page" structure matching Voynich's sections) might raise vocabulary
  and lower persistence. We did not tune them, and tuning them afterwards is not allowed under this test.
- **Possible reason for the persistence failure:** Voynich DEV mixes sections and Currier A and B. The generator
  makes one homogeneous text. A meaningful text that changes subject has the same property, so this failure points
  to "the text changes subject", which favours L or C but is not proof.
- **What this result is not.** It does *not* show that a real language can match all 13 features. No language
  text has been run through this same 13-feature comparison. That is the obvious next test, and it is just as
  likely to embarrass L.
