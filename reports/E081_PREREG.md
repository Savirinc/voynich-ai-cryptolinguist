# E081 pre-registration (Hebrew campaign H3): the morpheme-code attack

Written 2026-10-27, before the run. Script `experiments/e081_hebrew_morpheme_code.py`; output
`experiments/results/e081.json`, `e081_run.log`; report section in `reports/HEBREW_CAMPAIGN.md`.

## Form H3
Hebrew hidden as a code of word pieces: a Voynich front piece stands for a Hebrew prefix (*ve-, ha-, be-, le-, mi-,
ke-, she-* and their pairs), a Voynich ending for a Hebrew suffix (*-im, -ot, -o, -ah, -nu, -tem...*), and each glyph of
the bridge for one root letter. Any piece may stand for any unit, and several pieces may stand for one unit
(homophones); the attack is not told which slot maps to which.

## Units
- **Hebrew** (hboWLC, marks removed as E052): each word → optional prefix (longest of וה וב ול ומ וכ וש ה ו ב ל מ כ ש,
  leaving ≥ 2 letters) + root letters one by one + optional suffix (longest of ים ות יו יה הם הן כם נו תי תם ו ה י ך ם ן ת,
  leaving ≥ 2 letters). 71 unit types; the 40 commonest kept.
- **Voynich** (DEV, clean; E049 cleaning `n1`): each word → optional front (longest of qo q o d y s l, word longer than
  it) + bridge glyphs (S3 units) + optional ending (longest of aiin ain iin in edy eey ey dy y ol or al ar am m r l s o
  d). 63 unit types; the 40 commonest kept (896 of 89,706 units dropped).
- Language model: 4-gram Kneser–Ney over Hebrew unit sequences with word spaces (books GEN–2KI); plaintext for cracks
  from EZK, PSA, PRO, JOB, 1CH, 2CH.

## Attack and rules (E063 rules; settings E047 except 60,000 iterations per restart, 32 restarts, 40 symbols)
Tasks: 2 cracks (Hebrew unit text enciphered with the E047 encoder: random homophone key over 40 symbols weighted by
Voynich unit frequencies, 12% slips), 2 generator controls (Timm & Schinner seeds 31, 32, cut into units the same way),
5 pseudo-Voynich-A controls (order-2 Markov over Voynich units), Voynich A; 5 pseudo-Voynich-B controls, Voynich B.
VALIDATED iff both cracks reach accuracy ≥ 0.80 and agreement ≥ 0.95 and the lower crack lexrate exceeds every
A-control's; T = midpoint. CLAIM iff validated, agreement ≥ 0.95, lexrate ≥ T and > the relevant control maximum + 0.05.
Lexrate = share of decoded words of ≥ 3 units that are Hebrew words of the model's vocabulary.

| Outcome | Next | Campaign |
|---|---|---|
| CLAIM | blind reading by Hebrew readers, then a LOCKED_TEST prediction | none until confirmed |
| NO CLAIM, validated | — | H3 excluded on A and B within scope (these unit cuts, 40 symbols, many-to-one) |
| NOT VALIDATED | a pre-registered amendment may raise effort once | H3 untested |

## Disclosed
E080 (H1, H2 no claim); E079 (Voynich's pieces do not pair cleanly with Hebrew's by behaviour); unit inventories and the
dry-run task list above. No attack has been run. One attempt at this setting.
