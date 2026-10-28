# E094 pre-registration (Test A, Arham): is the later hand's month identification right, and what does each zodiac picture show?

Written 2026-10-28, before any judge has seen an image. Scripts: `experiments/e094_build_zodiac_images.py` (image sets),
`experiments/e094_score.py` (scoring). Judges' answers: `experiments/results/e094_judges/`. Output `experiments/results/e094.json`,
report `reports/ZODIAC_PICTURES.md`. No ledger factor (this tests the anchor, not M/L/C).

## Question
A later hand wrote month names on the 12 zodiac pages (mars, aberil ×2, may ×2, yony, iollet, augst, septembre,
octembre, novembre, decembre). Arham: "somebody who wrote aberil on one page would have noticed something to call it
that"; we presume the identification is correct. (1) Do blind readers of the pictures alone, with the month names
painted out, reach the same signs? (2) Which features carry each sign, and how much damage do they survive? (3) Beyond
the sign: what in each picture relates to names, zodiac, sun sign, astronomy, astrology (figures, rings, stars, tubs,
clothing, what could the arrangement represent)?

## Materials (built by the locked builder, seed 94094)
- 12 zodiac pages from the DEV canvases already on disk (1006200–1006207; leaves 70–73, none LOCKED_TEST).
- **FULL**: the whole circular diagram (1,600 px). **CENTRE**: the central medallion (800 px), at six levels: L0 clean,
  L1 blur r6, L2 blur r14, L3 pixelated to 40 px, L4 grey + strong noise, L5 cut into 4×4 shuffled tiles.
- The later-hand month name on every page is painted over with the local parchment colour; also the f73v marks at the
  top left ("C" strokes) and the small "A" on f72v2. Images carry random codes; the key is
  `experiments/results/e094_key.json`, outside the image folder (`data/external/e094_images/`).

## Judges
Fresh general-purpose sub-agents, each with no other context, one condition each: **FULL ×3, CENTRE_L0…L5 ×2 each**
(15 judges). Each reads the 12 images of its condition (listed in a judge-specific random order) and writes a JSON file.
Prompt (FULL; CENTRE omits the fields marked *, and says "the central part of a circular diagram"; degraded levels add
"some images may be blurred, noisy, pixelated or cut into shuffled tiles"):

> In the folder DIR there are 12 images: LIST. Each shows a circular diagram from an old illustrated manuscript. Some
> small rectangular patches were painted over on purpose; ignore them. Look at every image with the Read tool. Do not
> open any other file or folder and do not search the web. For each image, first describe what you see, then decide.
> Write a JSON file to OUTPATH: {"images": {"img_XXX": {"description", "central_figure" (plain words),
> "zodiac_sign" (one of the 12 sign names, "not a zodiac sign" or "cannot tell"), "confidence" (1–5), "sign_reason"
> (which visible features decide it), *"n_human_figures" (integer estimate), *"rings", *"figure_details" (clothing,
> tubs or barrels, what they hold, posture), *"celestial_objects" (stars, sun, moon, how many), *"groupings",
> *"astro_concept" (what astronomical or astrological idea the arrangement could represent, e.g. degrees of a sign, days
> of a month, decans, stars or constellations, planets, seasons, months, and why), *"other"}}, "recognise_source":
> answered only after all images: do you recognise which manuscript these come from (yes/no, which)}. "cannot tell" is a
> valid answer. Reply "done" when the file is written.

## Scoring (locked `e094_score.py`)
- Expected sign per page = the sign the month name implies under the annotator's own pairing (mars→Pisces, aberil→Aries,
  may→Taurus, yony→Gemini, iollet→Cancer, augst→Leo, septembre→Virgo, octembre→Libra, novembre→Scorpio,
  decembre→Sagittarius).
- Per page, votes of the 5 clean judgements (FULL ×3 + CENTRE_L0 ×2); majority = most votes, a tie is no majority.
  **ANNOTATION CONFIRMED** iff the majority matches on >= 10 of 12 pages; PARTLY CONFIRMED 6–9; NOT CONFIRMED <= 5.
- Sensitivity: the same excluding any judge who says it recognises the manuscript (an AI may recall the answer; the
  describe-first protocol and the masking limit but do not remove this).
- Degradation: per page and level, judges (of 2) naming the expected sign. Descriptive.
- Context (descriptive): per page, the FULL judges' figure counts, rings, figure details, celestial objects,
  groupings and astro concepts, beside the E073 counts (figures, tubs, clothing, head cover, hand on star).

## Disclosed
- The analyst has seen all 12 drawings (to map canvases, place the masks and check that no month name remains). Masks
  also cover a little drawing (part of the Scorpio animal's legs, a figure edge and the start of a ring word on f73v).
- Some FULL crops include a sliver of the neighbouring page on fold-outs (f72r1, f72r2); its month name is masked too.
- Prior knowledge: the identifications are standard in the literature (voynich.nu; E010B used them); f74 (Capricorn,
  Aquarius) is missing.
- Scorer smoke-tested on random fake judge files (deleted).
