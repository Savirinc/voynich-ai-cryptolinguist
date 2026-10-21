# E031 (ledger test 2): exact copies and near-copies together — A LANGUAGE DOES BOTH (one text, a primer)

Pre-registration: `reports/E031_PREREG.md` (sha256 2fec8313…aeed, locked before the run). Script
`experiments/e031_copy_pairs.py`. Result: `experiments/results/e031.json`, log `e031_run.log`.

## Plain-language result
- **The premise holds.** Voynich's near-copies are attracted, not chance: NR = 2.14, so neighbouring words one glyph
  apart are 2.1× more common than if the words were shuffled. Exact copies: R = 2.65.
- **Each habit alone is found in real texts.** Exact copies above 1.5× chance appear in 5 of 153 texts (Indonesian,
  Malay, Czech, Telugu, Hebrew). Near-copies above 1.5× appear in 8 (mostly Hebrew, Latin, Czech, Polish).
- **Both together are found in exactly one text of 153:** `cs_59765`, *Čítanka pro školy obecné* (1870s), a
  **Czech children's reading primer**.
  - Its near-copies are spelling drills: *me se*, *li la*, *dá vá*, *ne ní*.
  - Its exact copies are drilled vocabulary: *tráva tráva*, *louka louka*, *růže růže*.

By the pre-registered rule that is **A LANGUAGE DOES BOTH**, so **L × 3**. The rule is applied as written.

## Caveat: this result hangs on one unusual text
- The only text that does both is not ordinary language use. It is a teaching book that drills syllables and
  words.
- The other high-near-copy texts are telling too:
  - a **Latin reader** (*The Gate to Cæsar*, NR 2.95), where abbreviations make the near-copies;
  - **Hebrew** legal texts (NR 2.12–2.97), with short unvocalised words and one-letter prefixes.
- If that primer is set aside as "not ordinary language", the result would be NO LANGUAGE DOES BOTH, and the update
  would go the other way (M × 3).
- We do **not** set it aside; we never exclude after the fact. The ledger records both versions so the fragility is
  visible.

| | M | L | C | O |
|---|---|---|---|---|
| before E031 | 0.28 | 0.56 | 0.13 | 0.03 |
| **after E031, as pre-registered (L × 3)** | **0.13** | **0.79** | **0.06** | **0.01** |
| if the primer were not counted (M × 3) | 0.54 | 0.36 | 0.08 | 0.02 |

## What the test did teach us (no update, observations)
- Ordinary prose in 36+ languages, and every Bible, has *both* R and NR below about 1. Voynich is above 2 on
  both.
- The real texts that come near Voynich are **drill, list or abbreviation texts**: primers, readers, legal texts with
  sigla. A real-language Voynich would have to be of that *kind of text*, not ordinary prose.
- That is a concrete, testable lead: genre, not language. It is noted, not yet tested.
