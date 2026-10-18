# E025 (methodology A4): Voynich's line effects are produced by no tested system

Pre-registered: reports/E025_PREREG.md (sha256 0e4648d8…). Script: experiments/e025_line_effects.py.
Results: experiments/results/e025.json. 3,338 Voynich DEV lines; 20 twin samples per family.

| | V_first (first glyph, line-initial vs medial) | V_last (last glyph, line-final vs medial) | LEN_first | LEN_last |
|---|---|---|---|---|
| **Voynich** | **0.391** | **0.327** | 1.09 | 0.95 |
| word | 0.081 (z +37) | 0.035 (z +38) | 1.32 | 1.01 |
| compound | 0.067 (z +25) | 0.027 (z +57) | 1.19 | 1.02 |
| Naibbe, no line rule | 0.046 (z +52) | 0.025 (z +60) | 1.12 | 1.02 |
| Naibbe, fitted line-end m | 0.046 (z +48) | 0.231 (z +6.5) | 1.12 | 0.98 |
| Rugg grille | 0.067 (z +61) | 0.031 (z +50) | 1.16 | 1.02 |
| Self-citation | 0.064 (z +42) | 0.162 (z +12) | 1.28 | 1.12 |

**Verdict: the line is a functional unit.** Which glyph a Voynich word starts or ends with depends strongly on
whether it stands at the start or end of a line: 4–15× more than in any system tested, including the two with a
deliberate line rule. Only LEN_last is matched (by plain words).

## Consequences (as pre-registered)
- Every Stage B decoder needs a line model: line-initial and line-final transformations, validated on twins. A
  decoder that ignores lines misreads every line-initial and line-final word, about 2 words in 9.
- Medieval scribal practice gives natural candidates: line-final abbreviation and suspension marks, line-initial
  decorated or substituted letters (Voynich paragraph-first lines start with gallows), and filling a line to its
  end. These are hypotheses for Stage B, not findings.
- Limit: Voynich paragraph-first lines (gallows-initial) are included; they add to V_first. Splitting them out is a
  reported follow-up, not a change to this result.
