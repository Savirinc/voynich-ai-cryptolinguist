# E116 pre-registration (Arham, move 2, 2026-11-01): do repeated phrases appear once the spelling families are merged?

Script `experiments/e116_merged_phrases.py` (sha256 in the commit). Locked before the Voynich is scored.

## Question
The Voynich has almost no repeated phrases: Q3 10.8 is BETWEEN (E100), and it has no repeated 4-word sequence at
all. Real texts reuse many. There are two explanations:
- **Free spelling:** the same word is written in several spellings chosen freely (the five alternations e/ee, r/l, t/k,
  d±, q±; E037–E039, E059). That would break phrase repeats.
- **M:** there are no phrases to repeat.

If the first is right, merging each spelling family into one form should make language-level phrase reuse appear.

## The merge (declared now; no other variant)
- **The five steps:**
  - drop a word-initial q;
  - drop every d;
  - l → r;
  - k → t;
  - any run of e → one e.
- **Empty words:** a word left empty becomes "_".
- **Applied to:** the Voynich and every control written in EVA, the copy generator and the dice books, so M is
  merged exactly as the Voynich is.
- **Meaningful texts are used as written.** Merging can only cost a real text phrase repeats: if anything, this
  favours finding PHRASES APPEAR.

## Data and statistic
- **Voynich:** DEV prose lines (E099/E100 shape), 28,841 tokens, 6,077 types; **3,478 types after merging**. The type
  count was computed in development to set the band; no phrase count was.
- **Statistic:** E100's Q3 = (repeated 3-word tokens + 1) / (the same after shuffling + 1), in the Voynich line shape.
- **Meaningful:** the 69 E099 texts.
- **Generator (all merged):**
  - copy generator: 10 E032 stretches and 50 E100 grid stretches;
  - 10 dice books: E114's best set, 2d6 with new tables every page, lists 20/60/40.
- **Matching:** only controls whose types are within ±15% of the *merged* Voynich's types (2,956–4,000).

## Validity (known answers)
- At least 10 matched generator texts (G*) and at least 8 matched meaningful texts (L*).
- The L* Q3 p10 must exceed the G* Q3 maximum.
- From E100's numbers, 15 meaningful texts are in this band.

## Decision table
| Outcome | Rule | Factor |
|---|---|---|
| PHRASES APPEAR | merged Voynich Q3 ≥ L* p10 and > G* max | M × 1/3 |
| NO PHRASES | merged Voynich Q3 ≤ G* max and < L* min | M × 3 |
| BETWEEN | otherwise | none |
| VOID | validity fails | none |

**Rule 8:** if Q3 is within 0.5 shuffle-sd of a boundary, 10 fresh shuffle seeds must agree (≥ 8 of 10), else BETWEEN.

## Unscored
- **Power check:** the matched meaningful texts with five planted free spelling variants, not merged back. How far do
  their raw repeated triples (RP3) fall? This shows whether free spelling *can* hide phrases.
- **RP4** (repeated 4-word tokens) after merging.
- **Each merge step alone** on the Voynich.

## Seen beforehand
- **Known:** the Voynich's unmerged Q3 10.8, RP3 236, RP4 0 (E099/E100).
- **Development (smoke, controls only):**
  - merged generator Q3 0.8–3.9 in or near the band;
  - one generator setting with no glyph check (`none`) gives 20.4 at 6,901 merged types, outside the band;
  - the power check raised Q3 for some texts while their richness rose, because Q3 rises with richness. So the power
    check is read on raw RP3.
- The merged Voynich type count (3,478) was computed to set the band.
