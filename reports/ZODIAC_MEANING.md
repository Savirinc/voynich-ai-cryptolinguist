# E095 (Test B): do the zodiac words carry their own sign's meanings?

Pre-registration `E095_PREREG.md` (sha256 44f015f9…), script (sha256 fb9a1ca9…), meaning lists
`reports/data/e095_concepts.json` (sha256 5bd4f969…). Results `experiments/results/e095.json`, log `e095_run.log`.
Run 2026-10-28, 43 s.

## Verdict: VOID (calibration failed)
The test had to find planted sign words before its Voynich result could count:
| Planted language | Pages covered with the right meanings | Wrong-meaning maximum | p | Needed |
|---|---|---|---|---|
| Latin | 11/12 | 10 | 0.010 | <= 0.01 ✓ (just) |
| French/Occitan | 9/12 | 11 | 0.93 | ✗ |
| Hebrew | 12/12 | 11 | 0.010 | ✓ (just) |
| Latin, half the signs planted | 10/12 | 10 | 0.02 | descriptive |
Even a fully planted answer barely stands out, and the French/Occitan plant does not stand out at all.

**Why the test is blind.** A free letter key over about 90 words per page can fit almost any 4–9-letter meaning
somewhere. Wrong meanings cover 8–11 pages anyway, so a right reading has almost no room to show. The zodiac pages hold
too little text to identify a key from meaning matches alone. This agrees with the E010 anchor power analysis (anchors
too few and too weak to identify a key).

## Voynich (unscored, because VOID)
Every configuration sits at its wrong-meaning average: right pages 3–11 of 12, against null means 3.5–10.9.
- The best of the 32 configurations is Catalan, glyph groups, zodiac-only words: 7 pages vs 5.6, p 0.03 alone.
- Combined over all 32 (max-T 2.66), p = 0.16. That is what chance gives with 32 tries.
- No sign of the right meanings on the right pages, but a VOID test cannot be counted as a negative either.

## Language-free part (descriptive)
Pages sharing a planet, element or season do not share more vocabulary or glyph patterns, apart from one weak case:
| Shared attribute | Words (Jaccard) | Glyph trigrams |
|---|---|---|
| Planet | −0.004, p 0.70 | −0.043, p 0.97 |
| Element | −0.003, p 0.70 | +0.023, p 0.10 |
| Season | **+0.014, p 0.012** | +0.005, p 0.36 |
Season/words is the only low value, but it does not survive correction for six tests (Holm bar 0.0083). It may also
reflect the tubs and clothing style break inside the spring signs (E094) and neighbourhood vocabulary rather than meaning.

## What it means
- **Matching meanings word by word on the zodiac pages cannot work at this text size,** whatever the language. Even a
  planted answer is hard to see.
- **The anchor (Test A) is solid,** but it carries too little information to unlock a letter key on its own.
- **A powered version needs at least one of three things:**
  - more anchored text (e.g. the plant pages with secure identifications, combined with the zodiac);
  - a much narrower key family (one sign per letter, no many-to-one);
  - a stronger statistic (total matched letters rather than pages covered).

  Each would be a new pre-registered test.
- No ledger factor.
