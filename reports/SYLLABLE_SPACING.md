# E044: are Voynich's spaces between syllables? — NO (syllable-spaced texts avoid adjacency too)

Pre-registration `reports/E044_PREREG.md` (sha 99164c33…4698, commit 916a3ec). Script
`experiments/e044_syllable_spacing.py`. Results: `experiments/results/e044.json`, `e044_run.log`.

| Text (8,806-token windows) | SL | AS | Distinct units | Fits A / B? |
|---|---|---|---|---|
| **Voynich A** | **1.60** | **1.10** | **2,702** | |
| **Voynich B (A-size)** | **1.98** | **1.03** | **2,390** | |
| Vietnamese (syllables) | 1.21 | 0.25 | 964 | no / no |
| Chinese characters | 1.01 | 0.31 | 933 | no / no |
| Mandarin pinyin | 0.86 | 0.29 | 613 | no / no |
| Latin (words) | 0.98 | 0.02 | 2,608 | no / no |
| Indonesian (words, doubling) | 1.89 | 1.37 | 1,551 | no / no (types) |

**Verdict (pre-registered): SYLLABLE TEXTS AVOID ADJACENCY TOO.** SYLL-UNIT × 1/3, so the spacing sub-hypothesis
moves from WORD-UNIT 0.80 / SYLL-UNIT 0.20 to **0.92 / 0.08**.

## Plain reading
1. **Syllable-spaced writing does not explain C21.** Vietnamese and Chinese also avoid putting identical units side by
   side (AS 0.25–0.31), only less strongly than word-spaced Latin (0.02).
2. **Syllable-spaced writing also has far too few distinct units** (600–960 against Voynich's 2,400–2,700 at the
   same size), confirming E028. Voynich's spaces most likely separate **words**.
3. **The only text reaching Voynich's AS is a language with grammatical doubling** (Indonesian, 1.37). But its
   vocabulary is too small, and its doubling is a back-to-back spike (E043 exploratory profile), unlike Voynich's
   flat profile.
4. **Outside language, the copy generator came closest** (0.76, E043).

C21 is therefore a property that **no tested writing system or text type reproduces**: not prose, verse, hymns,
scripture, recipes or herbals, and not syllable-spaced writing. It is now among the strongest constraints on any
explanation.
