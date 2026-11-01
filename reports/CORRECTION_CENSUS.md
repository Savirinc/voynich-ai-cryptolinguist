# X121: correction census (Arham, step 2; exploratory, unscored)

Images: IIIF from the Beinecke, DEV pages only, at 1,200 px plus high-resolution crops.
- Stored in `data/external/correction_census/` (gitignored).
- f85r1 was skipped: its fold-out canvas carries the locked leaf f86.
- No locked leaf and no f102 canvas was requested.

## Why it is unscored
There is no known-answer control:
- We have no locally imaged manuscript of a real copied text, nor a handwritten gibberish text, from which to measure
  correction rates.
- No published correction count for the Voynich exists (`WEB_SWEEP.md`, physical sweep).

So this is a description, not a test.

## What the transcription records (ZL 3b, DEV prose and labels)
- **Marked corrections:** 16 transcriber marks `corr?` in 28,841 words, about **1 per 1,800 words**.
- **Gaps:** 8 `gap` notes (layout gaps, mostly f89r2).
- **Line intrusions:** 3 "next line intrudes" notes.
- **Words added later:** one page (f58v) has words "scribbled in afterwards" at a line end.
- **Word-level repairs:** none marked on any DEV page (no word inserted above a line, no word struck out).

## What the images show at the marked spots (6 located of 15)
| Spot | EVA | Seen |
|---|---|---|
| f16r.2 | otey | one glyph inside the word re-inked in darker ink |
| f19r.2 | @241; (line end) | one glyph covered by a heavy dark blot (overwritten) |
| f27r.6 | chol{oh}aiin | a glyph reshaped mid-word (o joined to a following stroke) |
| f39r.12 | tolchda[iin:ii?] | the word ending blotted in darker ink |
| f50v.8 | qo'd | no visible correction (a mark only) |
| f93v.6 | ytch[?:o]l | ink spatter beside the word; no rewrite visible |

The other spots were not located with confidence at this resolution and were not classified.

## Reading
- Every visible correction is **glyph-level**: one sign re-inked, blotted or reshaped, usually in darker ink. That may be
  later retouching (Stolfi's retouched pages; `WEB_SWEEP.md` #11).
- None is **word-level** of the kind a copyist of a real text typically makes: an eye-skip repaired, a word added
  above the line, a duplicated word struck out. The one eye-skip claimed in public (f105r) is on a locked leaf and was
  not examined.
- This fits a writer who never lost his place in an exemplar, which is what M predicts. A very careful copyist would
  look the same. Without control rates it cannot be scored.
- **What would make it a test:** correction rates and kinds from (a) 15th-century copied herbals and (b) handwritten
  gibberish produced under similar conditions.

No factor; ledger unchanged (M 0.9130, L 0.0612, C 0.0116, O 0.0142).
