# E050: the Hebrew near miss — explained by surface statistics; no meaning found

Pre-registration `reports/E050_PREREG.md` (sha de269c7f…76e5, commit 66eb4b5). Script
`experiments/e050_hebrew_nearmiss.py`. Results: `experiments/results/e050.json`, `e050_run.log`,
`e050_passages.json`, `e050_labels.json`, `e050_judges.json`.

## Part 1: statistics (Hebrew LM, E047 attack)
| Text | lexrate |
|---|---|
| **Voynich A** (3 seeds, identical) | **0.542** |
| 20 pseudo-Voynich-A texts (Voynich's signs and word shapes, no language) | 0.507 – **0.550** (median 0.530) |
| 20 copy-generator samples | 0.367 – 0.521 (median 0.417) |
| Positive control: real Hebrew in a secret 23-sign script | 0.621 (accuracy 1.000) |

**VOYNICH A DOES NOT BEAT ALL CONTROLS.** It sits in the middle of the pseudo-Voynich texts. Its E049 "near miss"
is what any text with Voynich's sign frequencies and short words gets under a Hebrew model. **It contains no evidence
of Hebrew.**

## Part 2: blind reading
Two independent judges (fresh Claude sub-agents, the exact pre-registered prompt, no tools) scored 7 unlabelled
passages for meaning (0–10):

| Passage | What it was | Judge 1 | Judge 2 |
|---|---|---|---|
| C | **Positive control: real Hebrew** | **9** | **10** |
| D | Voynich f3r decoded | 1 | 1 |
| F | Voynich f2v decoded | 1 | 1.5 |
| G | Voynich f2r decoded | 1 | 1 |
| A, B, E | Pseudo-Voynich controls decoded | 1, 1, 1 | 1, 1, 1 |

- **Both judges are VALID:** each recognised the real Hebrew instantly, and both even identified it as 2 Kings
  22:18–20, through the encoding and spelling slips.
- **Verdict (pre-registered): NOT DETECTED.** Both judges called all three Voynich pages "word salad", meaning real
  short words (house, built, sons, and-to, what) with no phrases or grammar, exactly like the fake texts.

**Disclosure:** before the judges answered, I recognised passage G as Voynich, because its opening words match the
E049 sample printed earlier. The judges had no such information.

## Conclusion (pre-registered overall rule)
**Hebrew, written letter by letter in a Voynich-like 23-sign script (the validated VOY23 class): searched, not
found.**
- The statistical near miss is explained by surface shape.
- The decoded pages carry no meaning, while the same method and judges recovered real Hebrew perfectly.

**This does not exclude Hebrew in other forms:** syllabic signs, abbreviation, a different word segmentation,
non-Biblical vocabulary under heavy encoding, or several layers.
