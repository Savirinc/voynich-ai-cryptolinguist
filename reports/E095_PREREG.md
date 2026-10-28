# E095 pre-registration (Test B, Arham): do the zodiac words carry their own sign's meanings?

Written 2026-10-28, before the true page-to-sign assignment was scored. Script `experiments/e095_zodiac_meaning.py`,
meaning lists `reports/data/e095_concepts.json`. Output `experiments/results/e095.json`, `e095_run.log`, report
`reports/ZODIAC_MEANING.md`.

## Question
Test A confirmed the picture side: each zodiac page is one sign, its figures are the sign's degrees, and the later
month names fit (with a one-month convention question). Arham: search the zodiac words not only for "April" but for
the whole context around each sign (month, sign, animal, planet, element, season), in many languages, aggressively.
**Is there one letter key under which the zodiac pages contain words for their OWN sign's meanings more than for
other signs' meanings?**

## Meanings (fixed in the JSON before matching)
Per sign: both months (the annotator's, e.g. Aries = April, and the 15th-century Julian one a month earlier, Aries =
March), sign name, animal or figure, ruling planet, element, season, in **Latin, French/Occitan (with the annotator's
spellings), Catalan, Italian, German, Greek (romanised), Hebrew and Arabic** (consonantal, one letter per consonant;
Hebrew months by the Sefer Yetzirah pairing). Targets of at least 4 letters.

## Words and keys
- W1: each page's zodiac-only words (345 types in all; `ZODIAC_ONLY_WORDS.md`). W2: all clean words of each page
  (labels and ring text).
- Units: K1 EVA letters; K2 glyph groups (S3: ch, sh, cth, iin, ee, qo, dy …).
- A key maps each unit to one letter (several units may share a letter). A word matches a target if, decoded, it equals
  the target (exact) or the target's first n >= 6 letters (abbreviation), forwards or backwards.
- **Score** = pages (0–12) holding at least one word that matches a target of that page's own sign. The key is found by
  greedy consistent construction with 300 random restarts.

## Test
- **Null:** the same search with the 10 signs' meaning sets shuffled among the signs (two-page signs stay together),
  99 permutations per configuration; this asks whether the right pages fit better than wrong pages. It controls false
  claims by design (meaningless text has nothing page-specific).
- **32 configurations** (8 languages × K1/K2 × W1/W2), combined by max-T (each configuration standardised by its own
  null; the same max taken for every permutation). **CLAIM iff p(max-T) <= 0.01**, followed (before any reading is
  reported as such) by a seed check of the best configuration (10 fresh searches, >= 8 of 10 at p <= 0.01) and a
  blind reading. NO CLAIM otherwise.
- **Calibration (power), run first:** one planted sign word per page (random key) in W2 for Latin, French/Occitan and
  Hebrew (K1): each must give p <= 0.01, else VOID. Latin with half the signs planted is reported as descriptive power.
- **Language-free part (descriptive):** do pages sharing a planet, element or season share more words (Jaccard) or
  glyph trigrams (cosine)? Same-sign and adjacent pages excluded; 9,999 permutations of signs.
- **Ledger:** none for NO CLAIM (the searched form is narrow; recorded in the Hebrew/zodiac campaign notes). A CLAIM
  moves nothing until the seed check and a blind reading confirm it.

## Disclosed (seen before locking)
- The analyst saw the zodiac words (E010B; `ZODIAC_ONLY_WORDS.md`) and the pictures (E094).
- **Tuning on nulls only.** A first optimiser (annealing) was too weak; it was replaced by greedy restarts. Null-only
  runs (shuffled assignments, never the true one) showed that with 3-letter targets and 4-letter abbreviations a wrong
  assignment covers 10–12 of 12 pages for W2 (no room for a signal). With targets >= 4 letters and abbreviations >= 6,
  wrong assignments cover about 8–10 (W2) and 4–7 (W1) pages. These settings were then fixed. Short targets
  (mars, leo, sol, aer, ver, may as 3 letters) are therefore excluded; that is a real loss of aggressiveness, accepted to
  keep the test able to detect anything.
- Expected runtime about an hour.
