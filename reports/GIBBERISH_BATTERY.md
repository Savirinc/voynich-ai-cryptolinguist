# E068: human gibberish against Voynich's other small-scale habits — M RULED DOWN, M × 1/3

Pre-registration `reports/E068_PREREG.md` (sha256 a935a638…3a5a68), script `experiments/e068_gibberish_battery.py`
(sha256 1dc977db…d7aa54), locked in the commit before the run. Results `experiments/results/e068.json`,
`e068_run.log`. 23 s.

## Verdict
Five of six features are diagnostic (Voynich and the typical language are told apart at 150 tokens). **Gibberish is
Voynich-like on one of the five (near-copies) and language-like on four** (word-length spread, letter predictability,
ending concentration, back-to-back repeats). Not borderline. Pre-registered: **M RULED DOWN, M × 1/3.**

**Plain reading.** People writing gibberish invent plenty of fresh words (E067), but the words they invent look like
words of their own language: loosely shaped, unpredictable letter by letter, with endings spread over many letters,
and they almost never write the same word twice in a row. Voynich words are tightly shaped, highly predictable inside,
end in five letters nine times out of ten, and repeat back to back. On those four habits the gibberish pages sit with
the Bibles, not with Voynich. The copy generator has the opposite profile: it gets the word shapes, the predictability,
the endings and the near-copies, but not the vocabulary (E032, E064) and only part of the repeats. **No meaningless
process we can test has both halves.**

## Numbers (150-token windows)
| Feature | Voynich (sd) | Languages (60) | **Gibberish (36)** | Generator | Diagnostic? | Gibberish is |
|---|---|---|---|---|---|---|
| WL, mean word length | 5.01 (0.32) | 4.98 | 4.91 | 4.60 | no | — |
| WLSD, spread of word length | **1.71** (0.14) | 2.49 | **2.41** | 1.63 | yes | language-like |
| H2, letter predictability (bits) | **1.98** (0.15) | 2.74 | **2.98** | 1.84 | yes | language-like |
| END5, share ending in 5 commonest letters | **0.93** (0.04) | 0.76 | **0.62** | 0.93 | yes | language-like |
| R, back-to-back repeats ÷ chance | **1.28** (0.17) | 0.16 | **0.55** | 0.79 | yes | language-like (between) |
| NR, near-copies ÷ shuffled | **1.23** (0.10) | 0.53 | **1.31** | 1.23 | yes | **Voynich-like** |

(R at 150 tokens is lower than the full-scale 2.65 because chance is computed within the window, not within the line;
all groups are measured the same way.)

## Reading
- **Gibberish writers do near-copies.** Writing a word and then a near-variant of it is a human habit (NR 1.31, even
  above Voynich's 1.23), which the languages do not share (0.53). This is the one Voynich habit human gibberish
  reproduces besides vocabulary, and it is the habit E031 could find in no ordinary language.
- **They do not repeat exactly** (R 0.55, half of Voynich, close to E045's AS 0.66), and they do not make Voynich's
  rigid word shapes. The rigidity (WLSD, H2, END5) is where the copy generator and Voynich agree against both humans
  and languages: it looks like a *system* of word-building, not free invention. E027's caveat applies: measured in
  glyph groups rather than EVA letters, Voynich's H2 and WL move into the simple-syllable language range; END5 and R
  do not depend on that choice.
- **Where M stands after E067–E068.** Human free gibberish gives vocabulary and near-copies; the copying machine gives
  word shapes, endings and near-copies; neither gives exact repeats at Voynich's rate, and neither gives everything.
  A meaningless Voynich would need a disciplined invented word-system (machine-like rigidity) used by a human who also
  invents freely (human-like vocabulary) and doubles words on purpose. That is not excluded, but it is a conjunction,
  and the ledger charges it.

## Ledger
| | M | L | C | O |
|---|---|---|---|---|
| Before (after E067) | 0.1932 | 0.7788 | 0.0245 | 0.0036 |
| **After E068** | **0.0739** | **0.8938** | **0.0281** | **0.0041** |

From the range edges (M 0.87, L 0.07 after E067): M 0.69, L 0.17, C 0.12. The two-horse picture is unchanged: L
ahead at the point values, M ahead from the edges, M's two wins and one loss today all weak by design.

## What this does not cover
Line-level habits (gibberish pages have lines, Bibles do not; not tested), book-scale vocabulary (no sample long
enough), and the unit question (EVA letters vs glyph groups) for WL, WLSD, H2.
