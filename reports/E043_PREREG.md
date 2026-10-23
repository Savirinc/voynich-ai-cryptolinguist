# E043 pre-registration: which kind of text makes words recur within a line? (sacred vs practical vs other)

Written 2026-10-23, before the run. Script: `experiments/e043_line_recurrence.py`. Updates `reports/LEDGER.md`: new
sub-hypotheses within L.

## Background (an exploratory finding, disclosed)
While answering a question about "double words", I ran an unregistered check, shown in full in the conversation and
summarised here.
- Voynich's excess of exact repeats is **not specific to back-to-back position**. A word meets a copy of itself
  about 3× chance at distances 1, 2 and 3 alike.
- Shuffling the words *within each line* leaves the rate unchanged (2.72 against 2.65 observed).
- In contrast, real doubling languages (Indonesian, Malay) spike at distance 1 only.
- Latin, Czech and Turkish show about 1× within lines.
- Biblical Hebrew showed about 3× at distances 2–3 but not at distance 1.

So C9 ("words repeated back to back") is better described as **"words recur within the same line"**. This test asks
which *kind of text* does that, including the owner's hypothesis that Voynich is a sacred or religious book.

## New sub-hypotheses within L (set now, before any result)
| Sub-hypothesis | Meaning | Share of L |
|---|---|---|
| L-sacred | religious, liturgical or scriptural content (prayer, hymn, ritual, scripture) | 0.30 (range 0.15–0.45) |
| L-practical | a medical, herbal, astrological or recipe handbook | 0.45 (range 0.30–0.60) |
| L-other | anything else: literary, records, mixed | 0.25 (range 0.15–0.35) |

**Why these shares.** The pictures (plants, jars, zodiac, bathing) match well-known secular 15th-century genres,
which favours L-practical. But the owner's sacred reading is coherent, and the near-total absence of religious
imagery cuts both ways.

## Texts (fixed now)
| Group | Texts |
|---|---|
| **SACRED** | Latin hymns (Hymni et Cantica, Ambrose's hymns, Prudentius's Peristephanon); Latin Psalms (Vulgate); Hebrew Psalms (WLC); Latin Genesis–Exodus; Hebrew Genesis–Exodus |
| **PRACTICAL** | Apicius + Cato + Varro (recipes, farming; = E034); Columella (farming); Culpeper's herbal (English, PG #49513) |
| **OTHER** | Vergil, *Aeneid*; Ovid, *Metamorphoses*; Caesar, *Gallic War* |
| Reference (not scored) | Indonesian Bible (real doubling) |
| GENERATOR | The Timm & Schinner copy generator (E032 output, 10 seeds, its own lines) |

## Statistics
- **SL (same-line recurrence):** the rate at which neighbouring words are identical *after shuffling words within
  each line* (mean of 5 shuffles), divided by chance (Σp²). This measures how often a word has a copy of itself
  somewhere in its line.
- **AS (adjacency specificity):** the observed back-to-back repeat rate ÷ (SL × chance). About 1 means back to back is
  not special; well above 1 means real doubling.
- **Also reported:** the observed repeat rate at distances 1, 2 and 3 ÷ chance.

**Lines.**
- Each reference is cut into pseudo-lines following Voynich DEV's own sequence of line lengths, from a random start,
  so that line length is equal across texts.
- The generator keeps its own lines.
- Natural lines (verse lines, Bible verses) are reported as a secondary result.

**Windows.** Non-overlapping chunks of Currier A's token count (8,806), up to 10 at random (seed 43043).

**Target.** Voynich DEV (all). A and B are also reported.

**Match.** z = (V − mean) ÷ max(own sd if at least 3 windows, median sd of all references with at least 3 windows,
2%|V|, 0.01). A text MATCHES if |z| ≤ 3 on both SL and AS.

## Decision
| Outcome | Rule | Bayes factor |
|---|---|---|
| ONLY SACRED MATCHES | at least one SACRED text matches; no PRACTICAL or OTHER text does | L-sacred × 3 |
| ONLY PRACTICAL MATCHES | likewise | L-practical × 3 |
| ONLY OTHER MATCHES | likewise | L-other × 3 |
| ONLY THE GENERATOR MATCHES | the generator matches; no language text does | M × 3 |
| MIXED or NOTHING MATCHES | otherwise | none |

**The factors are weak (×3)** for three reasons:
- the groups have unequal numbers of texts (5 sacred, 3 practical, 3 other), which gives sacred more chances;
- every text is Latin, Hebrew or English, not Voynich's language;
- line length is simulated for all texts except the generator.

## What was seen before writing this (disclosed)
- The exploratory distance profile above, for Voynich, Indonesian, Malay, Latin (Vulgate), English (KJV), Hebrew
  (Genesis region), Turkish, Czech and Swahili, at one seed.
- **None** of the other texts in this file (hymns, Psalms, practical texts, verse, prose, the generator) has been
  measured on these statistics.
