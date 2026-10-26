# Label-class programme, step 0: where the o-tall-letter words sit in a line (descriptive, unscored)

Run 2026-10-26. Script `experiments/label_step0_line_position.py` (recipe and reading rule written in its docstring
before any result was seen). Output `experiments/results/label_step0_line_position.json`. DEV prose only; LOCKED_TEST
leaves excluded.

## Question
The label words (o + tall letter + short core + ending) are 4–6% of running text. Reading 1 of the label-class programme
(list words / pointers such as "item", "idem") predicts that they open lines and entries. Reading 4 (quantities)
predicts that they stick to particular neighbours. Readings 2 and 3 (names, abbreviations) predict neither.

## Sets measured in prose
| Set | Word types | Prose tokens |
|---|---|---|
| OG: every prose type starting o + t/k/p/f | 659 | 3,596 |
| ZL: zodiac label types starting o + gallows, as they occur in prose | 70 | 1,970 |
| SH: the 25 label types shared by pharma and zodiac labels | 25 | 1,293 |

Control: 500 draws replacing each type by a random non-member of the same frequency bin; 95% band reported.

## Result
| Measure (ALL) | OG | control band | ZL | control band | SH | control band |
|---|---|---|---|---|---|---|
| line-initial share | **0.056** | 0.094–0.148 | **0.034** | 0.054–0.141 | 0.069 | 0.040–0.141 |
| line-final share | 0.118 | 0.091–0.146 | 0.104 | 0.060–0.138 | **0.186** | 0.050–0.138 |
| mean relative position | **0.560** | 0.465–0.519 | **0.569** | 0.456–0.535 | **0.578** | 0.455–0.549 |
| previous word ends in -y | 0.422 | 0.372–0.509 | 0.425 | 0.322–0.538 | **0.296** | 0.312–0.608 |
| previous-word concentration | 0.034 | 0.042–0.064 | 0.046 | 0.048–0.079 | 0.062 | 0.047–0.087 |
| **reading (pre-set rule)** | EVEN | | EVEN | | EVEN | |

Currier A and B agree in direction (A's bands are wider; OG line-initial A 0.107 vs 0.095–0.165, B 0.037 vs
0.083–0.152). The SH line-final excess comes from `am`, `dy`, `y` (known line-final words); the 15 o-gallows members
of SH are inside their bands on every measure (line-initial 0.042 vs 0.021–0.169).

Context from other classes (200 draws): gallows-initial words open lines (0.339 vs 0.095–0.150); ch/sh-initial words
avoid line starts (0.035 vs 0.112–0.149); other o-words are at chance (0.104 vs 0.086–0.150); qo-gallows words follow
-y words (0.746 vs 0.293–0.384) but have no line preference.

## What it means for the programme
- **Reading 1 (list words / pointers) loses its main prediction:** the label words open lines *half* as often as
  matched words, and open paragraphs a third as often (0.006 vs 0.020). They sit slightly late in the line. A list
  marker that never opens an entry is not a list marker. Reading 1 is set aside without a full pre-registration; its
  secondary prediction (repetition at entry starts) has nothing left to stand on.
- **Reading 4 (quantities) gets no help:** no neighbour concentration (previous-word concentration at or below the
  control band in every set).
- **Readings 2 and 3 (names, abbreviations) survive** as predicted: even distribution, no lock to neighbours.
- The line-start avoidance is part of Voynich's known line system (gallows words open lines, ch/sh words do not); it is
  a fact about the class, not evidence for any reading.

No ledger factor (descriptive pass, agreed as such on 2026-10-25).
