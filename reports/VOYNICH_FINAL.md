# The Voynich search: final report (2026-10-21)

The search stops here under the stop rule fixed in advance (`reports/FINAL_ROUND.md`, locked, sha256 80833efb…).
The last remaining small-key family, syllable notation over Latin, Italian, French and German, was excluded by a
key-free test (E029a, `reports/WORD_REPEATS.md`). No confirmed claim was produced.

## The conclusion
**Within every family we could test, over Latin, Italian, French and German, the Voynich text does not decode.**

Two key-free facts together close the main routes:
1. **Voynich words are not pieces of plaintext words** (E019): word-level topic clustering, z +12.7. This rules out
   letter ciphers and Naibbe-type verbose ciphers, whatever their tables.
2. **Voynich words are not whole plaintext words either** (E029a): Voynich repeats words back to back 70 times more
   often than any of 973 la/it/fr/de texts. This rules out word-for-word codes of every kind, including large
   codebooks. The locked plan had still listed those as possible.

So, if the text has meaning, it is in one of these:
- a **mixed system**, for example a word code plus filler words that repeat;
- a **language or text type** outside these four, with natural word repetition. E027/E028 found simple-syllable
  languages fit the glyph statistics but have far too few distinct words;
- a **system outside every class we could test**.

Otherwise it is **meaningless**. Our mechanical gibberish generators (Rugg grille, self-citation) fail on other
features (E011, E019, E021), but human-written gibberish remains fully open.

We do not claim the text is meaningless. We claim that no system we could test reads it, and we name exactly which
ones.

## What was tried (complete record)
| Road | Family | Where | Result |
|---|---|---|---|
| A (small key) | letter substitution, mono and homophonic, 9 unit inventories, 36 languages | E012 | no answer (valid at 2 inventories) |
| A | any fixed-key letter cipher | E019, E021 | ruled out |
| A | plain alphabet over any glyph grouping | E012, E024 | ruled out |
| A | Naibbe verbose cipher, published tables, la/it/fr/de | E016–E018 | NO CLAIM, 12/12 |
| A | Naibbe verbose cipher, unknown tables | E019 | ruled out (topic clustering) |
| A | plain simple-syllable language | E027, E028 | inconsistent (vocabulary too small) |
| A | syllable notation, each word kept (family F), la/it/fr/de | final round, E029a | ruled out (word repeats) |
| — | word codebook, stem + ending code | Stage B dev; E029a | could not prove themselves (dev); ruled out for la/it/fr/de prose (E029a) |
| B (anchors) | all known anchors; zodiac months; same-month pages; plants | E010–E010D, E022–E023 | insufficient or negative |

Full experiment list: `reports/SUMMARY.md`. Every test was pre-registered, locked and hash-recorded before it ran.
The 15 LOCKED_TEST leaves were never used.

## What the work did establish (positive findings)
- A validated method: a known-answer attack (E016–E017) that reads Naibbe-type ciphers of unseen text and flags its
  own failures. It also produced no false claims on controls.
- Structural facts about Voynich that any future theory must explain:
  - word-level topic clustering (E019);
  - glyph statistics typical of simple-syllable writing when glyph groups are read as units (E027);
  - Latin-sized vocabulary (E028);
  - about 28 endings (E026);
  - line effects (LINE_EFFECTS);
  - adjacent word repeats 70 times above European prose (E029a).

## What would reopen the search
Only a new fact, not a new idea, per the Occam rule (`reports/OCCAM.md`). For example:
- a real anchor, meaning a word whose meaning is known independently;
- a period text whose word repetition and vocabulary match Voynich's;
- evidence of filler words, such as specific repeating words that behave differently from all others.

## Next
Work moves to the Indus script, as agreed.
