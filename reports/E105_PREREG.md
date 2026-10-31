# E105 pre-registration: vowel harmony with o, a, y as vowels (Arham, Reddit idea R11, 2026-10-31)

## Question
A Reddit post (4hmqxa) suggests that Voynich *o*, *a* and *y* act as vowels that agree within a word, as in vowel
harmony (Turkish, Hungarian). Do Voynich words show vowel-to-vowel agreement beyond what the positions of the glyphs
in the word give, at the level of real harmony languages and above the copy generator?

## Data and procedure (`experiments/e105_vowel_harmony.py`)
- **Units:** word types of a 28,841-token cut (Voynich: DEV clean prose, with LOCKED_TEST leaves excluded).
- **Statistic:** I = mutual information (bits) between consecutive vowels within words, with consonants skipped.
- **Null:** vowels are permuted among words within cells of (word length, character position), 20 permutations. This
  keeps where vowels sit in a word, which matters for the Voynich's rigid slot order, and destroys word-level
  agreement. EXCESS = I − mean null.
- **Vowels:**
  - languages: letters whose NFD base is one of a e i o u y, plus ı, ə, æ, œ;
  - Voynich and generator: *o, a, y*.
- **Known answers:**
  - harmony: Turkish (turytc), Hungarian (hun), Azerbaijani (azb);
  - non-harmony: 22 Latin-script languages (latVUC, ita1885, deu1912, ces1613, polubg, eng-kjv, fraLSG, nld, dan1931,
    swe, ron1924, hrv, slk, lit, indayt, tglulb, hausa, mri2012, haw1868, cebulb, hil, iloulb). Bantu languages,
    Yoruba and Ewe are left out because they have partial harmony.
- **Generator:** 60 stretches (E032 × 10, E100 grid × 50).
- **Validity:** the lowest harmony-language EXCESS > the highest non-harmony EXCESS.

| Outcome | Rule | Factor |
|---|---|---|
| HARMONY-LIKE | Voynich EXCESS ≥ harmony minimum and > generator maximum | M × 1/3 |
| NO HARMONY | Voynich ≤ non-harmony maximum | none (most languages lack harmony, so absence is not evidence for M) |
| BETWEEN | otherwise | none |
| VOID | validity fails | none |

- **Rule 8:** if the Voynich is within 0.5 permutation-sd of a boundary, run 10 fresh permutation seeds; at least 8
  must agree.
- **Unscored:** the Voynich with *o, a, y, e* as vowels.

## Seen beforehand
- The Reddit claim; E065 (no syllabary); E040 and E041 glyph profiles. No Voynich harmony value has been computed.
- **Smoke run** (no Voynich):
  - harmony: Turkish +0.925, Hungarian +0.516, Azerbaijani +0.839;
  - non-harmony: Latin +0.031, Italian +0.039, German +0.154;
  - generator: +0.008 to +0.015.
