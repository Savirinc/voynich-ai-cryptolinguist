# X117: where does the surprise sit? (Arham, move 3; exploratory, unscored)

Script `experiments/e117_surprise_map.py` (results `experiments/results/e117.json`, dev run `e117_dev.json`, logs
`e117_dev.log`, `e117_run.log`); follow-ups `experiments/x117_followups.py` (`x117_followups.log`).

## Question
In a real herbal, the information (the surprise) gathers where the content is: the plant name at the start of
each entry. In a gibberish process it should be spread evenly. Does the Voynich's surprise gather anywhere?

## Measure
- Every text is cut into its own real entries:
  - Voynich pages;
  - Bible chapters;
  - Culpeper herb entries (heading dropped);
  - copy-generator pages (29 lines, the generator's page unit);
  - dice-generator pages (E114 best set, refilled per page).
- Surprisal of a word = −log2 p(word) under a word-frequency model built from all the *other* entries. It is high when a word is rare outside its own entry.
- HEAD = mean surprisal of tokens 2–11 of each entry minus the mean over the rest of the entry. Token 1 is skipped everywhere, because of the Voynich's paragraph-initial gallows (E106).

## Development (controls only, before any Voynich number)
| Group | HEAD |
|---|---|
| 61 Bibles (chapters) | −1.21 to +0.25, p10–p90 −0.72..+0.09 |
| Culpeper's herbal (entries) | **+0.74** |
| 60 copy-generator runs (pages) | −0.39 to +0.52; random-source settings +0.21..+0.52 |
| 10 dice books (pages) | −0.05 to +0.08 |

The bands overlap: Bible chapter openings are *less* surprising than the rest, and several generator settings are
positive. So HEAD is no yardstick between language and gibberish in general, and the test was **not locked**.
Its verdict is VOID by construction and carries no factor.

The only meaningful text with herbal-style entries (Culpeper) does show the predicted rise. One text makes no band.

## Voynich (unscored map)
| | Surprisal (bits) |
|---|---|
| **HEAD (page openings minus rest)** | **+0.89** (jackknife sd 0.11): above all 132 controls, including Culpeper and every generator |
| Herbal / bathing / stars / pharma pages | +0.81 / +0.78 / +0.90 / +0.55 |
| Same, with the five spelling families merged (E116) and gallows unified (k, t, p, f → t) | +0.52 (= the top generator setting; below Culpeper) |
| Line 1 of page / lines 2, 3, 4+ | 12.0 / 10.4, 10.2, 10.4 |
| Paragraph-first lines: at page top / mid-page / all other lines | 11.7 / 11.1 / 10.2 |
| Word position in line: first / middle / last | 11.7 / 10.1 / 11.5 |
| Label words (scored by the prose model) vs prose | 12.0 vs 10.1; 29% of labels never occur in prose |

**Page-unique words** (used on no other page) among tokens 2–11 vs the rest:

| Text | Tokens 2–11 | Rest |
|---|---|---|
| Voynich | 0.236 | 0.136 |
| Culpeper | 0.094 | 0.047 |
| Generator, err5_random | 0.211 | 0.143 |
| Generator, default | 0.112 | 0.105 |

## Reading
- The surprise in the Voynich gathers at the **top line of each paragraph**, most of all the first line of the page. It
  also gathers at the two ends of every line, and in the labels. Below the first line the page is flat.
- About 40% of the page-opening rise goes away when the known first-line glyph habits (gallows, the spelling
  alternations) are merged out. What is left (+0.52) sits at the top of the generator range.
- So the map is consistent with either reading:
  - a herbal-like "name first" layout;
  - a scribal habit of writing special word forms in the first line, as the generator's random-source settings partly do.

  This test cannot tell them apart.
- **For crib work (move 5),** the high-information slots are the paragraph-first lines (page top first), line ends and
  labels.

No factor; ledger unchanged (M 0.8860, L 0.0803, C 0.0151, O 0.0186).
