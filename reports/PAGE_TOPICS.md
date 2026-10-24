# E054 (picture route 4a): are herbal pages about different things? — VOID (the generator also does it)

Pre-registration `reports/E054_PREREG.md` (sha 54c4d098…dcf8, commit be927f7). Script
`experiments/e054_page_topics.py`. Results: `experiments/results/e054.json`, `e054_run.log`.

D is the share of the topic change that happens at the page boundary (1 = a new page brings a new subject; 0 = the
boundary is not special).

| Text | Pages | within | across | distant | D |
|---|---|---|---|---|---|
| Voynich herbal A | 76 | 0.256 | 0.216 | 0.171 | **0.47** |
| Culpeper, real plant pages | 300 | 0.331 | 0.291 | 0.281 | 0.80 |
| Culpeper, fake boundaries | 299 | 0.304 | 0.329 | 0.297 | −3.54 |
| **Copy generator** (its own 29-line pages) | 304 | 0.330 | 0.194 | 0.141 | **0.72** |
| Voynich herbal B | 32 | 0.213 | 0.192 | 0.161 | 0.40 |
| Voynich stars paragraphs | 247 | 0.103 | 0.090 | 0.050 | 0.25 |

**Verdict (pre-registered): VOID, no factor.**
1. **The copy generator shows a strong page effect (0.72).** Timm & Schinner's generator works page by page, so its
   vocabulary also shifts at page boundaries. The prediction that a generator has "no boundary effect" was wrong for
   this generator, so the test cannot separate reference from that kind of gibberish.
2. **The fake-boundary control is unstable.** For Culpeper, within-page and distant similarity are almost equal, so
   the ratio blows up (−3.54). D is a fragile measure for long, formulaic entries.

**Unscored observations:**
- Voynich herbal pages do change vocabulary at page boundaries (D 0.47; across 0.216 lies between within 0.256 and
  distant 0.171).
- Real plant pages and the page-wise generator both do the same.

**Lesson.** Page-level topic structure does not tell meaning from a page-aware generator. The picture route needs tests
that tie *specific words* to *specific drawn objects* across different parts of the book, for example the same plant
drawn in the herbal and pharmaceutical sections. That requires the images or a published list of visual matches.
