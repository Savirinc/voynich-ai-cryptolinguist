# E077: are labels odd in the bridge (like foreign names) or everywhere? NOT ODD (known answer passed; no factor)

Run 2026-10-27 under `E077_PREREG.md` (locked). Script `experiments/e077_label_oddness.py`; results
`experiments/results/e077.json`, log `e077_run.log`. Arham's option 3.

## Known answer: Latin names behave like names
4,361 Latin name types (32,895 tokens: Phison, Hevilath, Gehon, Euphrates, Adam...) against length-matched rare Latin
words:
| Slot normal rate | names | rare words | excess oddness |
|---|---|---|---|
| ending in the 20 common endings | 0.58 | 0.92 | 0.34 |
| bridge known from ordinary words | **0.08** | 0.47 | **0.40** |
z(bridge) +126, z(bridge − ending) +12.5: **NAME-LIKE**. Foreign names carry unknown bridges. VALID.

## Voynich labels
1,081 label tokens against length-matched rare prose words (frequency 1–2):
| Slot normal rate | labels | rare prose words | excess oddness |
|---|---|---|---|
| front present | 0.83 | 0.63 | −0.19 (labels *more* normal: the *o-* of *ot/ok*) |
| ending in the 20 common endings | 0.87 | 0.84 | −0.03 |
| bridge known from prose | **0.72** | 0.69 | −0.02 |
z(bridge) −1.15, z(ending) −2.13: **NOT ODD**.

## Reading
- Label words are built from the same fronts, bridges and endings as rare prose words. Their earlier "oddness" (five
  times more kit misfits than prose, 2026-10-27 count) is the oddness of rare words in general, not a special,
  foreign-looking stem.
- Foreign names, as the Latin check shows, would bring bridges the rest of the text never uses. Voynich labels do not.
  If labels are names, they are names built from native pieces (like English *Rose*, *Goodman*), not borrowed foreign
  names.
- No ledger factor (descriptive, working assumption L).
