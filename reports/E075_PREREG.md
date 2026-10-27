# E075 pre-registration: does swapping a word piece change the word's job the same way every time?

Written 2026-10-27, before the run, at Arham's direction: assume a language (Hebrew-like or Latin-like) and test, with
the front + middle + ending pieces, "how the meaning of them changes - even if we don't know the meaning at all".
Script `experiments/e075_piece_effects.py`; output `experiments/results/e075.json`, `e075_run.log`; report
`reports/PIECE_EFFECTS.md`.

## Idea in plain words
In a real language a grammar piece does the same job on every word: Hebrew *ha-* ("the") moves any noun after the same
kinds of words; Latin *-um* versus *-us* moves any noun into the same kinds of slots. So for a swap such as X → oX, the
change in the word's neighbours should point the same way across many different cores X. If it does, the piece is a
grammar piece, and the direction of the change says what kind of job it does, without knowing any meaning.

## Measure (identical for every text)
- Lines: Voynich DEV prose lines (28,841 tokens; LOCKED_TEST excluded); languages cut into the Voynich line lengths
  (E058 `pseudo`) from token 10,000; generator seeds 31–33 in their own lines.
- Kit: E074 recipe on the whole text: 10 fronts (0–2 characters), 20 endings (0–4).
- Swap pairs: front swaps a+X ↔ b+X and ending swaps X+a ↔ X+b between pieces of the kit, X non-empty, both forms with
  frequency ≥ 5. A swap pair is **eligible** with ≥ 8 cores.
- Context of a word: four probability blocks over its neighbours' pieces (previous word's front and ending, next word's
  front and ending; line edge counts as its own value). Shift d_X = context(b-form) − context(a-form).
- Consistency C = mean over cores of cosine(d_X, mean of the other cores' shifts). Null: random sign flips of the d_X,
  1,000 draws; z. A swap pair is **consistent** if z > 3.
- Per text: share of eligible swap pairs that are consistent.

## Texts
Voynich; languages hboWLC (Hebrew, consonants, marks removed as in E072), latVUC (Latin), deu1912, turytc, eng-kjv,
indayt; Timm & Schinner generator seeds 31–33. Shuffled controls: Voynich, Hebrew and Latin with words shuffled across
the text (lines kept).

## Validity
VALID iff Hebrew and Latin each have ≥ 5 consistent swap pairs and every shuffled control has a consistent share ≤ 0.05.

## Decision table
| Outcome | Rule | Ledger |
|---|---|---|
| **LANGUAGE-LIKE** | Voynich share ≥ the lowest language share and > the highest generator share + 0.05 | **M × 1/2** |
| **GENERATOR-LIKE** | Voynich share ≤ the highest generator share and < the lowest language share | **M × 2** |
| BETWEEN | otherwise | none |
| VOID | validity fails | none |
Weak factors because the share depends on how the automatic kit cuts words, and the generator is the only meaningless
process tested. Reported in any case: every consistent Voynich swap with its strongest shift (the "job" it does) and
examples, and Hebrew's and Latin's for comparison.

## Disclosed (seen beforehand)
- E074 and the Voynich kit build (pieces and coverage); E038 (q± same neighbours, r/l different neighbours); E059 (q
  after -y; d± follows line position and previous -y). These predict some consistent Voynich swaps (q, and r/l endings).
- Toy check before locking: a planted grammar swap scored z +5.6 to +6.2 and its shuffled version 0 of 49 pairs
  consistent; most toy swap pairs are cuts with no grammar (share 0.06), as expected from an automatic kit.
- No real text has been measured. One attempt (rule 9).
