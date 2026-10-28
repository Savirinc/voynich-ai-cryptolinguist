# E094 (Test A): is the later hand's month identification right, and what does each zodiac picture show?

Pre-registration `E094_PREREG.md` (sha256 3253f5d8…), amendment 1 (neutral image folder), builder and scorer locked;
judge answers `experiments/results/e094_judges/`, results `e094.json`, log `e094_run.log`. Run 2026-10-28, 15 judges.

## Result as pre-registered
**ANNOTATION CONFIRMED (12/12)**: all 5 clean judgements on every page name the sign the month name implies (mars →
Pisces, aberil → Aries ×2, may → Taurus ×2, yony → Gemini, iollet → Cancer, augst → Leo, septembre → Virgo,
octembre → Libra, novembre → Scorpio, decembre → Sagittarius).

## The major limitation: the judges were not blind
- **All 15 judges said they recognised the source** (the Voynich zodiac pages) when asked at the end.
- **The sensitivity analysis is therefore empty**: excluding recognisers leaves 0 judges, which the scorer prints as
  0/12. That is not a negative result, just no data.
- **The cause is structural.** The sub-agents run inside this project, so they load its CLAUDE.md, which names the
  manuscript and its zodiac pages (one judge said so). The neutral folder (amendment 1) could not prevent this.
- **What remains of the confirmation.**
  - The judges' own descriptions match the pictures, and the weak cases are exactly where the picture is ambiguous:
    the f73r "Scorpio" is a lizard-like animal with a curled tail and no claws (confidence 2–3); goat versus ram versus
    bull on the four horned animals; the Virgo figure holds a flower.
  - The strong cases are unambiguous to anyone: two fish, scales, two crayfish, a crossbowman, a couple holding hands.
  - So 9 of the 12 pictures carry their sign without any outside knowledge. Scorpio and the Aries/Taurus split rest
    partly on convention.
- **A truly blind check needs human judges** (or a model without project context).

## Damage ladder (centre medallion; correct judges of 2)
| Page | Sign | clean | blur | heavy blur | pixelated | grey + noise | shuffled tiles |
|---|---|---|---|---|---|---|---|
| f70v2 | Pisces | 2 | 2 | 2 | 1 | 2 | 2 |
| f70v1 | Aries | 2 | 2 | 2 | 0 | 2 | 0 |
| f71r | Aries | 2 | 2 | 0 | 0 | 0 | 2 |
| f71v | Taurus | 2 | 2 | 0 | 0 | 0 | 2 |
| f72r1 | Taurus | 2 | 1 | 0 | 0 | 2 | 2 |
| f72r2 | Gemini | 2 | 2 | 1 | 1 | 2 | 1 |
| f72r3 | Cancer | 2 | 2 | 0 | 0 | 0 | 2 |
| f72v3 | Leo | 2 | 0 | 0 | 0 | 0 | 0 |
| f72v2 | Virgo | 2 | 0 | 0 | 0 | 0 | 1 |
| f72v1 | Libra | 2 | 2 | 0 | 0 | 2 | 2 |
| f73r | Scorpio | 2 | 1 | 1 | 0 | 0 | 2 |
| f73v | Sagittarius | 2 | 1 | 0 | 0 | 0 | 2 |
The sign lives in small local details (horns, claws, the crossbow, the scale pans): cutting the picture into shuffled
tiles barely hurts, while pixelation destroys almost everything. Pisces (two fish) and Gemini (a couple) are the most
robust. Leo and Virgo, drawn in faint uncoloured line, are lost at the first blur.

## The whole context of each picture (full-page judges, descriptive)
- **Figures = degrees.** Judges' median counts: 15 on each of the four Aries/Taurus pages, 29–30 on the other eight.
  E073's independent count agrees exactly. Every figure holds or touches one star. All three judges read 30 figures as
  the **30 degrees of a sign** (or days of a solar month), and the 15-figure pages as **half a sign each**: Aries and
  Taurus are each spread over two pages, 15 + 15 = 30. This is the standard reading in the literature, and the
  pictures support it directly.
- **Two pictorial groups.**
  - *Spring signs (Pisces, Aries, Taurus-light; partly Taurus-dark):* half-length women in tubs or barrels; on f71r
    and f71v clothed, in red tunics and hats.
  - *From Gemini onwards:* nude full-length women standing or lying radially, no tubs. A few wear crowns or caps
    (f72v1 top, f73v).
  - The change from tubs to no tubs falls inside the Taurus pair (f71v tubs, f72r1 mostly none).
  - E073's BARREL notes disagree with the judges on f72v1–v3. E073's feature reliability was already found poor, so
    the judges' reading is given here.
- **Celestial objects.** One eight-pointed star per figure. Extra single stars sit beside the central figure on f70v2,
  f72v2 and f73r. No sun or moon is drawn on any page.
- **What the arrangement means astronomically (all three full-page judges agree).** A calendar of the zodiac by degree:
  each sign's 30 degrees as 30 star-holding figures, set in rings (the rings possibly halves or decans). The month
  names written later fit this: each page is the sign in which the sun stands for most of that month.

## What it means for Test B
The picture side of the anchor is sound. Each page is one sign, its 30 (or 15) figures are degrees, and the month names
are the right ones for those signs. The figure labels are therefore most plausibly **names of degrees, stars or
figures within a sign**, and the ring texts plausibly about the sign or month. Test B searches the zodiac-only words for
exactly this context (sign, month, planet, element, degree, star words) in many languages. No ledger factor (anchor
test).
