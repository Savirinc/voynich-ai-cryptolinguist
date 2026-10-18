# E021 (methodology A1c): do the most common Voynich words persist across the book?

Pre-registered: reports/E021_PREREG.md (sha256 bcafcf3d…). Script: experiments/e021_persistence.py.
Results: experiments/results/e021.json, e021_run.log. 720 twin samples.

Voynich DEV: PERS_30 0.264, COV_30 0.917 (Currier B: 0.345, 0.950).

| Family | PERS_30 (range) | z | COV_30 z | DEV | Currier B |
|---|---|---|---|---|---|
| word | 0.229–0.562 | −1.4 | −0.3 | consistent | consistent |
| compound | 0.218–0.593 | −1.4 | −0.3 | consistent | consistent |
| compound, ending tables by section | 0.200–0.534 | −1.1 | +0.4 | consistent | consistent |
| Naibbe, key per 4 sections | 0.246–0.464 | −1.2 | +0.8 | consistent | consistent |
| Naibbe, key per 8 sections | 0.162–0.278 | +1.9 | +3.1 | no (just) | consistent |
| words with strong spelling drift | 0.033–0.318 | +1.8 | +2.8 | consistent | no |
| syllable | 0.479–0.735 | −6.5 | −5.8 | no | no (−3.5) |
| Naibbe, fixed key | 0.661–0.766 | −16.9 | −8.3 | no | no |
| Rugg grille | 0.715–0.778 | −26.1 | −8.3 | no | no |
| self-citation | 0.117–0.203 | +4.0 | +4.7 | no | no |

**Pre-registered reading:** a changing-key Naibbe cipher is consistent, so A1c cannot separate it from words. A2 and
B1 must decide. The test does independently confirm the rejection of four families.

## Stage A1 so far (E019–E021 combined)
| Family | E019 word clustering | E020 glyph-pair clustering | E021 persistence | Status |
|---|---|---|---|---|
| Naibbe, fixed key (any tables) | rejected | — | rejected | **out** |
| Rugg grille | rejected | — | rejected | **out** |
| Self-citation | rejected | — | rejected | **out** |
| Syllable = word | rejected (DEV) | — | rejected | **out** |
| Word / compound | fits | glyph pairs too stable | fits | **in** (needs moderate scribe drift) |
| Changing-key Naibbe | not tested | too stable by > 11 SD | fits | in only if glyph inventory also changes |

Voynich behaves like word-sized units (whole words or stem + ending) whose common words persist like grammar
words, written with glyph habits that shift moderately along the book.
