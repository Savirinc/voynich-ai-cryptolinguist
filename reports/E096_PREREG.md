# E096 pre-registration: do the zodiac figure labels follow the period degree tables? (Route 2, Arham 2026-10-29)

## Question
Books of the Voynich era (the Arabic-Latin tradition of Alcabitius and Al-Biruni, as later tabulated by Lilly, *Christian
Astrology* 1647, pp. 116–118) give every degree of every sign a class: **gender** (masculine/feminine), **light** (light,
dark, smoky, void) and **term** (the ruling planet of a degree band, with bounds that differ from sign to sign). E094 found
that each zodiac page holds 30 figures, one per degree (15 + 15 for Aries and Taurus). If each figure's label names, or is
shaped by, its degree's class, then labels of figures in the same class should resemble each other more than labels of
figures in different classes, and they should do so for the RIGHT sign's table more than for other signs' tables.
No key and no language are needed.

## Data
- **Labels:** ZL 3b label lines on f70v2, f70v1, f71r, f71v, f72r1, f72r2, f72r3, f72v3, f72v2, f72v1, f73r, f73v.
  - One label line is one figure (30 per sign; 29 for Gemini).
  - The words on a line are joined.
  - Alternates `[a:b]` are taken as `a`; non-letters are stripped.
  - No locked leaves are involved (asserted).
- **Rings:** circle-text lines separate the label groups in ZL. These groups are treated as rings in ZL order.
- **Tables:** `reports/data/degree_tables.json`, parsed by `experiments/x097_parse_degree_tables.py` from
  skyscript.co.uk/deginf.html (Lilly's table; Al-Biruni variants marked but not used). Capricorn and Aquarius (no pages)
  serve as wrong tables only.
- **Not used:**
  - faces (decans), which split every sign identically into 1–10, 11–20 and 21–30, so they cannot be tested against
    other signs' tables;
  - deep, lame and fortune degrees, which are too sparse.

## Procedure (`experiments/e096_degree_tables.py`, seed 96196)
- **Label similarity:** Dice coefficient of glyph bigrams, with word-boundary marks.
- **Figure → degree mapping:** with n figures in an order, figure i gets degree ⌊30i/n⌋ + 1.
- **Orders tried:** ring order as listed or reversed × direction as listed or reversed × every circular start; for
  Aries and Taurus also page order swapped. That makes 120 orders per sign (240 for Aries and Taurus). The start of each
  ring and its direction are unknown, so every order is allowed.
- **Per sign and column:** D = mean similarity of same-class pairs − mean similarity of different-class pairs, maximised
  over the orders.
- **Column statistic:** the sum of D over the 10 signs.
- **Null:** the 12 sign tables are dealt to the 10 signs at random, with no sign getting its own table, and the same
  maximisation is applied (999 draws). For each column, z and p are computed against this null; max-T is taken over the
  3 columns.

## Known answers first
- **Calibration (planted labels):** for each column, 10 planted books.
  - Each degree's label is drawn from a pool of real zodiac labels; pools are defined by front piece (ot, ok, o, y,
    ch; one pool per class, chosen at random per sign).
  - A label comes from its own class's pool with probability 0.9, otherwise from another pool.
  - The planted labels are placed under a random hidden order.
  - **Required:** ≥ 8 of 10 planted books at p ≤ 0.01 in every column.
- **False-claim control:** the real labels against tables rotated by a random 1–29 degrees (all 12 tables), 20 draws.
  - **Required:** at most 1 draw with max-T p ≤ 0.01.

## Decision table
| Outcome | Verdict | Bayes factor |
|---|---|---|
| Calibration or false-claim control fails | VOID | none |
| max-T p ≤ 0.01 | DEGREE-TABLE LINK | M × 1/5 (labels that track a period table carry information) |
| max-T p > 0.01 | NO LINK | none (a narrow form; a meaningful text need not label degrees by class) |

A p within 0.5 sd of the bar (rule 8) is followed by a seed check: 10 fresh seeds of the null, ≥ 8 must agree. A LINK is
followed by the pre-registered check of which column and which signs carry it, then Arham's reading.

## Seen beforehand
- **The tables:**
  - the gender and light strings for all 12 signs, printed when the table was parsed;
  - the label lines of f73r, f70v1 and f72r2, printed when the ring structure was checked.
- **Earlier results:**
  - E056: labels are not numbers and do not repeat at the same ring position;
  - E073: same-label figures look no more alike;
  - E072: ot/ok behave as one piece.
- **Calibration development (synthetic only, no Voynich statistic computed):**
  - The first planted model used similarity clusters around random medoids at fidelity 0.8. It failed
    (2/10, 5/10, 2/10).
  - Front-piece pools at 0.8 gave 5/10, 10/10 and 6/10.
  - At 0.9 every column gave 10/10. The bar was set at 0.9.
  - **What this means for power:** the test can see a strong encoding, where about 9 in 10 figures follow the table. A
    weaker encoding (0.6–0.8) would often be missed. The cluster plant at 0.8 and the front plant at 0.6 are reported
    descriptively.
