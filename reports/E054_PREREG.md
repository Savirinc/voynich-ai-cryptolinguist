# E054 pre-registration (picture route, step 4a): are Voynich herbal pages about different things?

Written 2026-10-24, before the run. Script: `experiments/e054_page_topics.py`. Updates `reports/LEDGER.md`.

## Idea
In a real herbal, each page or entry is about **one plant**. When the page changes, the subject changes: new name, new
features, new uses. So the vocabulary shifts **at the page boundary** more than within a page. Two kinds of
meaningless process would behave differently:
- **A copy-from-recent-text generator** (Timm & Schinner) has no idea where pages end. Its vocabulary drifts
  smoothly, so there is no special shift at the boundary.
- **Shuffled or random text** has no structure at all.

This tests whether Voynich pages *refer to separate subjects*, which is the pictures' plant-per-page layout seen
through the text. It needs no language guess.

## Statistic
- Each page is split into a first and a second half (by tokens). Similarity is the cosine of the halves' word counts.
- **within:** first vs second half of the same page.
- **across:** second half of page i vs first half of page i+1.
- **distant:** pages at least 5 apart (500 random pairs, seed 54054).
- **D = (within − across) ÷ (within − distant):** the share of the topic change that happens *at the page boundary*.
  - About 1 means a new page brings a new subject.
  - About 0 means the boundary is not special.

## Texts
- **Voynich (primary):** herbal pages in Currier A (DEV, illustration type H, folio order): 76 pages, median 78 words.
- **Positive control:** Culpeper's *Complete Herbal*, one "page" per plant entry (340 entries; those shorter than 152
  words are dropped), each truncated to follow the Voynich page-size sequence.
- **Fake-boundary control:** the same Culpeper text cut at boundaries shifted by half a page. Its D should be about 0.
- **Meaningless control:** the copy generator (E032 output), pages of 29 lines, truncated to the same sizes.
- **Secondary (reported only):** Voynich herbal B pages, and the paragraphs of the stars section (each starred
  paragraph looks like a separate item).

## Decision
**VALID** only if all three controls behave as required:
- Culpeper real pages: D ≥ 0.5;
- Culpeper fake boundaries: D ≤ 0.2;
- copy generator: D ≤ 0.2.

| Outcome | Rule | Factor |
|---|---|---|
| VOID | the controls fail | none |
| PAGES ARE ABOUT DIFFERENT THINGS | Voynich herbal A D ≥ 0.5 | M × 1/3 |
| NO PAGE STRUCTURE | D ≤ 0.2 | M × 3 |
| PARTIAL | otherwise | none |

**Why only ×3.** A human hoaxer drawing a new plant on each page might also change their invented words page by page,
so a high D is not proof of meaning. It does rule out the copy-generator kind of gibberish.

## What was seen before writing this (disclosed)
- Herbal A page counts and sizes.
- Culpeper's entry headings, and the number of entries parsed (340).
- No similarity has been computed on any text.
