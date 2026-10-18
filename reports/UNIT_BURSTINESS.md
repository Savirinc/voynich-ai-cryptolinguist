# E019 (methodology A1): what does one Voynich word carry?

Pre-registered: reports/E019_PREREG.md (sha256 d00a9da0…; includes a disclosed protocol slip). Script:
experiments/e019_unit_burstiness.py. Results: experiments/results/e019.json, e019_run.log. 400 twin samples.

## Result (primary: DEV, 28,841 words)
| Family | I_word (Voynich 0.387) range | top_word (Voynich 0.285) range | z (I_word, top_word) | Verdict |
|---|---|---|---|---|
| word = word | 0.271–0.712 | 0.302–0.548 | −0.2, −2.3 | **survives** (favoured) |
| word = syllable | 0.059–0.242 | 0.073–0.418 | +6.2, +1.1 | rejected (survives in Currier B: +3.5, +1.4) |
| Naibbe (1–2 letters) | 0.007–0.091 | 0.000–0.052 | +12.7, +18.6 | **rejected** |
| Naibbe, 4-language sources (upper bound) | 0.028–0.123 | 0.000–0.088 | +10.0, +9.5 | **rejected** |
| Rugg grille | −0.167 to −0.071 | 0.000–0.011 | +20.4, +28.3 | rejected |
| Self-citation | 1.547–1.766 | 0.877–0.927 | −21.3, −41.1 | rejected |

Currier B alone (19,490 words): word and syllable survive; Naibbe, Naibbe-max, Rugg and self-citation rejected.

**Pre-registered reading:** Voynich word types cluster by topic as strongly as real words do: 10–19 SDs more than
a Naibbe-type cipher, including its upper-bound variant. Voynich words carry word-sized (or at least
syllable-sized) units. The 1–2-letter verbose-cipher class is deprioritised, and the two meaningless generators,
as specified, do not reproduce it.

## Caveat, reported in advance as a feature (not used for the decision)
Within-word glyph pairs also cluster strongly in Voynich (I_sub 0.150; top_sub 0.58), above every natural-language
twin (I_sub ≤ 0.116 on DEV). Voynich's ratio I_word/I_sub ≈ 2.6 lies between the word twins (~5–7) and the
syllable twins (~1.5–2). Something changes spelling or glyph habits along the book: scribes, Currier A/B,
section-specific spelling, or a system whose tables change by section. None of the twins modelled such drift. A
cipher whose tables drift by section was not tested; it is the one way a letter-level cipher could still produce
this profile.

## Amendment (2026-10-18, after E020)
E020 showed that a Naibbe-class cipher whose key changes by section (8 sections) reproduces Voynich's word-level
clustering. The E019 rejection therefore applies to a cipher with ONE fixed key only. The clustering of glyph pairs
inside words (where Voynich exceeds every changing-key cipher by > 11 SDs) is what still argues against that class.
See DRIFT_COMPOUND.md.
