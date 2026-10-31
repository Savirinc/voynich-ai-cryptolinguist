# R16 (Arham, Reddit i6pktp): the f57v ring sequence, a descriptive check (no test, no factor)

**Source:** ZL 3b transcription, f57v (leaf 57, a DEV page, not locked), circle line 3.

**Finding: confirmed.** The third ring is 68 single signs, written as one 17-sign sequence four times in a row:

```
o l d r v x k m f @169;v t r @170; @171; y I @172;
o l d r v x k m f @169;v t r @170; @171; y c @172;
o l d r v x k m p @169;v t r @170; @171; y c @172;
o l d r v x k m p @169;v t r @170; @171; y c @172;
```

- **The two changes:**
  - **Position 9:** *f* in the first two copies, *p* in the last two. The ring is split into halves by an *f*/*p* swap.
    This bears on the open "p vs f" lead: here the two gallows look interchangeable, or they mark halves of the circle.
  - **Position 16:** *I* in the first copy, *c* in the other three. This may be a scribal or transcription variant.
- **Rare signs:** the sequence uses signs that hardly occur in running text:
  - *v* once in all prose;
  - *x* 22 times;
  - the special signs @169–@172 and *I* never.
- **Similar rings:** ring 5 holds a similar run of single signs (*o v l r m aiin d @170 c f s y l k x l r @171 …*).
  Rings 2 and 4 hold ordinary-looking words.

**What it means (no factor):** this ring is not running text. It is a cyclic list of 17 signs repeated around the
circle, with the *f/p* change at the halfway point, like a table, an alphabet or a numbering. Many of its signs belong
to a special set barely used in the main text. That fits several readings (a key or table, a numbering scheme,
decoration), so nothing is scored. It is a lead for the queued "p vs f" question.

## X109 follow-up exploration (Arham, 2026-10-31; unscored, descriptive)

**Transcriptions agree.**
- **All three show the four copies.** Takahashi reads position 9 as *f, f, p, p*, as ZL does, and position 16 as *c*
  in every copy (ZL's *I* in copy 1 is a reading variant).
- **Glen Claston,** in its own alphabet, reads position 9 as three forms: copy 1, copy 2, and copies 3–4 alike. It also
  reads copy 1 differently in a few other places (positions 3, 12, 15, 16).
- **Conclusion:** the second half of the circle differs from the first in every transcription.

**The innermost ring uses the same special signs in another order.**
- It begins *o v l r m aiin d @170 c f s y l k x l r @171* and then becomes ordinary words.
- 16 of its first 20 signs belong to ring 2's set, including *v* (once elsewhere in the whole text) and @170/@171
  (nowhere else in the book).

**Where the copies sit (full-resolution image of f57v, an allowed page;**
`data/external/beinecke_f57v/f57v.jpg`).
- **Start of the ring:** ring 2 starts at about 10:30 on the clock face, at a radial divider line beside the label
  *dairal*.
- **Copy starts:** the four copies begin at about 10:30, 2, 5 and 8 o'clock, so each occupies one quarter of the
  circle.
- **Faces:** the four faces in the centre sit at about 12, 3, 6 and 9:30. Each copy is therefore centred on one face.
  Position 9 (the *f/p* sign, drawn with a heavy filled loop) falls near the middle of each copy, beside its face.
- **The *f/p* split by face:** *f* sits by the top and right faces, *p* by the bottom and left faces.
- **Caveat:** positions were read by eye and are approximate.

**Link to f66r.**
- **Where the signs occur:** the special signs @169 and @172 occur only on f57v and in f66r's margin column of single
  signs (*y o s sh y d o f @169 x air d sh y f f y o d s f c @172 x t o @195 l r t o x p d*).
- **Same left neighbour:** in both places these two signs follow the same sign. f57v has *f/p @169* and *c @172*;
  f66r has *f @169* and *c @172*.
- **But not the same list:** the f66r column does not follow the 17-sign order, so it is not a copy of the ring.

**What this suggests (to be tested, not claimed):** the book has a small set of special signs, used in fixed pairs,
in a quarter-by-quarter cycle on f57v and in a list on f66r. That fits a notation (numbers, a calendar or compass
cycle, a sign table) better than running text. The *f/p* split between the two halves of the circle is the clearest
pointer to what *f* and *p* do.

## X111 ring measurement from the image (Arham, 2026-10-31; unscored)
**Method.**
- **Unrolling:** the centre of the ruled circles was fitted on the full-resolution image (1734, 1457 px), and ring 2
  was unrolled into a straight strip.
- **Reading:** every mark's angle was read by eye on 30° strips with a 0.1° scale (about ±0.7°).
- **Data:** the readings are in `reports/data/f57v_ring2_marks.json`. Angles run clockwise from 12 o'clock.

**1. There are 72 marks, 18 per copy, not 17.**
- The transcription token `@169;v` is two separate marks on the vellum: a hooked stroke, then a small *v*-like sign
  1.5–2.5° later.
- So each copy is *o l d r v x k m f/p @169 v t r @170 @171 y c @172*: 18 marks, 4 × 18 = 72.
- This agrees with Nick Pelling's count of 72, though not with his explanation (two signs merged into a fake gallows):
  here the extra mark is the one that the transcription itself joins.

**2. The spacing averages exactly 5°, but it is freehand, not an instrument scale.**
- **Spacing:** with 72 marks, the mean gap is necessarily 5.00°. The individual gaps vary from 1.5° to 10.5°
  (sd 1.4°, 28% of a step).
- **Layout:** the gaps follow the same layout in every copy. The pair *@169 v* is always close (about 2°), and *@170*
  and *@171* (the large compound sign) always take about 6.5–7°.
- **Copy lengths:** the copies are not equal. The copy written first, starting just after a faint radial line at
  about 303.5° (10 o'clock), spans 98.5°; the others span 89.5°, 84.5° and 87.5°. The scribe started wide and then
  squeezed the rest to close the circle.
- **Conclusion:** this is a written sequence fitted to a drawn circle, not marks at engraved, measured divisions. A
  hand-drawn copy of an instrument would also look like this, so it neither proves nor rules out an instrument.

**3. Each copy points at a face.**
- **Centres:** the copies are centred at about 5°, 89°, 176° and 260°. The faces sit at about 0°, 90°, 180° and
  270–285°.
- **The *f/p* mark** sits about 37–41° into each copy, at 349°, 84.5°, 174.5° and 254°: within about 5–15° of the
  face direction in every quarter.
- **Order of copies:** reading from the divider (the transcribers' start), the copies run *f* (10–1 o'clock, top),
  *f* (1:30–4:30, right), *p* (4:30–7, bottom), *p* (7:30–10, left). So *f* covers the top and right half and *p*
  the bottom and left half.
