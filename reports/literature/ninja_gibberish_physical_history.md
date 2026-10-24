# voynich.ninja survey: meaningless-text hypotheses, physical evidence, history

Compiled 2026-10-24 from about 50 threads, read through the forum's guest archive (`/archive/index.php/thread-N-P.html`) and WebSearch snippets. **Caveat:** guests see only the first post of each 10-post page; every other post reads "Register or login". Most long threads (2658 corrections, 2790 T&S, 4740 Retracer) were therefore only partly visible. Claims that came only from search snippets are marked *(snippet)*. Codes: L = meaningful language, plain or lightly encoded; M = meaningless; C = cipher or encoding of a meaningful text.

---

## A. Meaningless-text hypotheses

### A1. Rugg's table-and-grille (2004)
- **Claim.** The text came from sliding a Cardan grille over a table of prefix, stem and suffix syllables (ReneZ's summary, thread-3537).
- **Critiques.**
  - The Cardan grille is 16th-century, so the method is anachronistic (Sam G, https://www.voynich.ninja/thread-984.html).
  - A table and grille can be built for any text, so a reconstruction proves nothing (Sam G).
  - A grille produces uniform text "without artifacts" and cannot produce the section-level and page-level patterns (Anton, -JKP-, thread-984).
  - Rugg's output "doesn't look at all like Voynichese" (ReneZ, 2019 *(snippet)*).
  - matildarose's pre-registered 4-gate pipeline fails on all four gates when run on grille text (https://www.voynich.ninja/thread-5680.html).
- **ReneZ's own variant.** ReneZ's 3-table "next level" cipher (thread-3537) was tested by MarcoP. Splitting plaintext into 3-letter groups raises MATTR, lowers reduplication and lowers h2 to Voynich levels. It also makes words too long and short words too rare, and labels cannot be single plaintext words.
- **Bearing.** The forum treats the classic Rugg grille as dead. It counts against M only in that one specific form.

### A2. Timm & Schinner self-citation / autocopy (2014, 2019/2020 Cryptologia, 2023 Malta review)
- **Claim.** Each word is copied from a nearby earlier word, usually on the same page, often from the line above at the same position, and then altered. On this view, Zipf's laws, page-level "topics" and similar-word clusters all fall out as by-products.
- **Evidence the authors cite.**
  - 84.7% of word types connect into a single edit-distance-1 network, with a longest path of 21.
  - Edit distance between words grows with line distance.
  - Each page is dominated by frequent words that are mutually similar.
- **Critiques.**
  - **Emma May Smith** (https://www.voynich.ninja/thread-2790.html, thread-3647):
    - The generator produces non-existent words, over-produces rare words and lets line-initial words appear anywhere.
    - Some bigram frequencies are wrong (lt vs lk, oa vs ya).
    - The similar-pair observation follows trivially from rigid word structure.
    - The rules are never explained: "aesthetic" glyph rules are a closed box.
  - **nickpelling** (thread-2790): there are many hand-coded substitution cases in the code, which points to overfitting, and "ligatures" (ol, dy) are treated inconsistently.
  - **ReneZ** (thread-2790): the method is under-specified. How far back does the scribe look? How does copying start? Timm's reply is that every word re-seeds the process and the scribe had "complete freedom", which makes the hypothesis hard to falsify.
  - **MarcoP** (https://www.voynich.ninja/thread-3647.html): using Patrick Feaster's 10-slot line-position plots, real Quire 20 shows smooth positional preferences for ch-/sh- across the line, similar to Shakespeare's sonnets. T&S output is **flat**, as is typographically re-lined Dickens.
  - **kckluge** (https://www.voynich.ninja/thread-4035.html): T&S's claim that A and B form a continuum rests on cosine similarity in 7,000 dimensions, which suffers from the curse of dimensionality. **Pages separate A from B with 100% accuracy on the per-page frequency of EVA `ed`.** The ranges are 0.00–0.51% on Herbal A pages and ≥1.34% on Herbal B pages: a sharp gap, not a smooth drift.
- **Supporters.** RenegadeHealer (thread-3647) argues meaningless text is the proper null hypothesis. Stephen Carlson (thread-3476) argues the effort argument is weak, since hoaxes historically involve huge effort.
- **Torsten's critique of Bowern & Lindemann** (thread-3476, thread-3344): there are no repeated phrases (few repeated bigrams or trigrams; Tiltman, D'Imperio, Ito 2002). Frequent tokens vary from page to page in a way that function words do not.

### A3. New 2026 generators (the most relevant items for us)
**quimqu's "scribe"** (https://www.voynich.ninja/thread-6219.html, Oct 2026)
- **How it works.** The tables are learned from ZL3b.
  - About 35% of words are copied from the same page. The chance of picking a source halves every ~3 lines, with a preference for the word directly above, and about half of copies get one letter changed.
  - New words are generated glyph by glyph from a model conditioned on the previous 2 glyphs.
  - Each bifolio has its own habits (k/t, ch/sh, q-, dy/y, e vs no-e).
  - The start of each word is conditioned on how the previous word ended.
  - Line and paragraph rules are added on top (closers at line end, p/f in first lines).
- **Results.**
  - It reproduces **58 of 64** measures. A simpler 3-rule generator gets 33.
  - Trained on odd folios and tested on even ones, it gets 51/64. For comparison, real odd vs real even folios agree on only 55/64.
  - **Back-to-back repeats are 3.1× chance in the real text and 3.3× in the scribe.**
  - Words with a "twin" earlier on the same page: 64% real, 68% scribe.
  - Removing any one rule breaks some measures.
- **The six failures.**
  1. Raw exact-repeat rate is too high (0.9% real vs 1.2%).
  2. Repeats at distance 5 are too high (2.9× vs 3.8×).
  3. **Word-specific repetition avoidance:** 16% of common real words almost never follow themselves (dal, shey, saiin), while okaiin repeats at 5× chance. The scribe gives 21% because it "only knows families of words, not single words."
  4. Line-final -m in long lines (3.4× vs 1.9×).
  5. q- at paragraph start is slightly too high.
  6. Long words are too common: 7.4% vs 5.3%, from glued double endings such as shedytedy.
- **Two further findings.**
  - The e/no-e word share is shared across the **two halves of the same bifolio** (z = −7.0), not with the physically next page (z = −0.7). It behaves like the habit of a writing session, not like subject matter.
  - The cross-word link (end of word → start of next) matches **Matthew Schwartz's (Harvard)** reported 0.12/0.21 bits for hands 1 and 2. A forum portal news item says Schwartz argues the text is "iteratively generated gibberish". It also says readings by simple or verbose substitution, consonantal writing, abbreviation, codebooks and the Naibbe cipher fail on withheld pages across six candidate languages. I have not seen the paper itself.
- **Open control.** npcompl33t asked whether the same model fitted to Moby-Dick would pass equally well. That control has not been run.
- **Other generators:** tikonen's "least effort" token generator (thread-5920), the "one-page ledger" method (thread-5752) and Donald Fisk's bigram generator, which also gives Zipf (thread-4401, thread-3344).

### A4. Human gibberish (Gaskell & Bowern 2022; Bowern & Lindemann 2021)
- **Gaskell & Bowern, "Gibberish after all?"** Human-written gibberish varies widely and can match either natural language or Voynichese on most metrics *(snippet, thread-4848 / thread-4531)*. Voynich shows **positive autocorrelation of word lengths**: rare in natural languages, common in gibberish *(snippet, https://www.voynich.ninja/thread-4693.html)*.
- **Bowern & Lindemann's line "gibberish is by nature random".** Torsten attacks it (thread-3344, thread-3476), since their own p.5 experiment found that people make local repetitions too easily. cbowern replies that "gibberish" means no syntax, which is random from a linguistic standpoint.
- **Small samples.** MarcoP collected two ~1,000-word hand-made gibberish samples. Koen's fits Zipf and has language-like MATTR. MarcoP's is mostly hapaxes (thread-3344). Koen found writing 300 words of gibberish "extraordinarily difficult".
- **Replication.** magnesium (Naibbe cipher, thread-4848) says he has replicated Bowern & Gaskell's ML classifier. Search snippets report that the classifier puts most VMS transliterations closer to gibberish.

### A5. Glossolalia
- geoffreycaveney (https://www.voynich.ninja/thread-2667.html) uses Samarin's description of glossolalia: "strings of syllables… word-like… a facade of language". His example is the f88r/f99v label rows (oral, oraly, oldar, otoky, otaly), which look like a grammar drill, not plant names.
- Others call the term anachronistic.
- Fasano's "non-stochastic glossolalia" paper (thread-4294) is criticised for having no measures.

### A6. Discriminators proposed so far, all contested
| Statistic | Status on the forum |
|---|---|
| Zipf / brevity / Heaps | Dismissed: generators and Koen's hand gibberish pass (DonaldFisk, Torsten, MarcoP; thread-4401) |
| MATTR, reduplication | Gibberish and generators span the language range |
| Montemurro–Zanette keywords | Disputed: generators produce co-occurrence clusters, and Herbal A vs B share illustrations but not keywords (thread-1845) |
| Line-position profile (Feaster slots) | **T&S output flat, VMS structured** (MarcoP, thread-3647). Not yet run on quimqu's scribe |
| Word-specific self-repetition avoidance | **Failed by the best generator** (quimqu) |
| Word-length autocorrelation | Gibberish-like (Gaskell & Bowern) |
| Pre-registered permutation gates | matildarose: grille text fails, the VMS passes 3–5 "roots" (weak; thread-5680) |

Nobody claims a single decisive statistic. RenegadeHealer and nablator say outright that none exists, because "no test can identify meaninglessness in general".

---

## B. Codicology and physical evidence

### B1. Corrections and erasures
Main thread: https://www.voynich.ninja/thread-2658.html (9 pages), plus thread-3259 and thread-449.
- **Consensus.** There are few visible corrections, but not zero.
  - -JKP- says there are "a couple of places" with scraping but has forgotten the folios.
  - Helmut Winkler repeatedly asks for an actual list and says he sees no corrections on a shave.
  - Other guesses: about 12 candidates *(snippet)*, or "a couple per big-plant folio, up to half a dozen on dense pages" *(snippet; the poster calls it a guess)*.
  - Medieval corrections were usually expunction dots, not strike-outs (-JKP-, bunny, thread-3259).
- **Torsten's typology** *(snippet, thread-2658 p.4)*.
  - The most common correction adds a stroke: e→s, ch→sh.
  - Examples: **f82r.P2.24 `qoeeedy`→`qoesedy`**; **f75r.P.32 `chedy chedy`→`chsdy shedy`**.
  - **Frequent** word types were altered, not rare ones, which he says is the opposite of what natural-language correction should look like.
  - A reply suggests the scribe was breaking up runs of identical or near-identical words.
- **Torsten vs LisaFaginDavis** (Mar 2026, visible).
  - LFD lists Scribe-1 "mistakes": 7r line 1 (qko), 18r line 1 (cf), and the 3-shaped glyphs on 10r.
  - Torsten replies that f10r.P.8–12 start with qo, oy, oq, 3o, 3o: "local experimentation", not error.
- **Bearing.** If corrections really cluster on frequent words and break up repeats, that fits M (cosmetic editing) better than copying a meaningful exemplar, where errors are eye-skips and dittography on arbitrary words. The evidence is thin, uncounted and partly guessed. Current ledger weight: about 1.

### B2. Evidence of copying from an exemplar
- **Stephen Carlson's autograph-vs-copy brainstorm** (https://www.voynich.ninja/thread-3025.html).
  - For autograph: no exemplar of the text, drawings or script; layout effects (LAAFU, text fitted to the space).
  - For copy: the corrections, and a well-planned word structure.
- **ReneZ** (https://www.voynich.ninja/thread-4853.html): on f88r the left-most of six words around five plant parts is the container's label and was written in the wrong place. He concludes "the scribe was not aware of this", i.e. the scribe was copying without understanding.
- **Stolfi** (same thread): the Author must have drafted on paper, and an unsupervised hired Scribe made the clean copy.
- **Wladimir D** (https://www.voynich.ninja/thread-540.html): some lines were inserted or written bottom-up.
  - Emma reads one page as written in sessions: paragraph III stopped mid-word, with the ink and slope changing.
  - bvanheu (thread-5943) shows gallows of an upper line drawn over glyphs of the line below.
- **Zodiac centre figures** (Koen G via Mark Knowles, https://www.voynich.ninja/thread-3903.html): copied detail-for-detail from a model. The painter imitated shading "beyond his skill", and the closest parallels are the Lauber/Haguenau workshop. This is copying of *images*, not proof of copying text.
- **Bearing.** A draft-plus-clean-copy workflow is compatible with L, C and pre-drafted M alike. No eye-skip or homoeoteleuton has ever been demonstrated. That absence is weakly informative, because eye-skip is only detectable if one knows the text.

### B3. Text and drawings, layout, writing sessions
- **pfeaster** (https://www.voynich.ninja/thread-4377.html): a frayed pen leaves doubled strokes in **both the text and the drawing** on f6v, f44r and f17r. Text and picture of a page were probably made in the same session. Darker ink falls systematically on particular glyph parts (first c of ch, d, the loop of k, r/l after o/a/i), across hands.
- **oshfdk** (same thread): surveyed 1380–1439 manuscripts on digitale-sammlungen and found none with ink-density jumps like the VMS's.
- **MarcoP, "Lines interrupted by drawings"** (https://www.voynich.ninja/thread-2945.html, ZL transliteration, 751 image breaks).
  - Words before a drawing are short, and `s` alone is 5× more frequent there.
  - Words after a drawing almost never start with a gallows or q-, and y-/o- are elevated.
  - Image breaks behave partly like line breaks and partly like labels.
  - **The text reacts to the drawing**, so it was composed or written around an existing picture.
- **Quire 13 order** (https://www.voynich.ninja/thread-5134.html). dashstofsk says text came first on f79, f81 and f75. ReneZ says f84v needed the drawing first, and that text and drawings were "added concurrently".
- **Bearing.** In-situ layout effects show the text stream was shaped on the page. That is natural for in-situ generation (M) or in-situ encipherment (C). For L copied from a differently laid-out exemplar it would need re-flowing. Mild evidence against a plain copy.

### B4. Bifolio-level production signatures
- **npcompl33t** (https://www.voynich.ninja/thread-6182.html).
  - **Method:** per-page glyph transition matrices → Jensen-Shannon divergence → MDS. The result is a Guttman horseshoe.
  - **Bifolio agreement:** pages of the same bifolio differ by only 1.5–2.5% along MDS1.
  - **Sequence:** the ordering is the unique best of 181,440 orders.
  - **Quire checks:** the Quire 20 order matches Davis & Layfield exactly; Quire 13 comes out reversed.
  - **Interpretation:** a time gradient. Herbal B was made after Pharma and Cosmo, then interleaved with Herbal A.
  - **Supporting views:** MarcoP: binding order correlates with MDS1 at −0.66, so A came before B. quimqu: change happens in steps between hands and sections.
- **Bearing (important for us).** The statistics follow the **writing session**, not the subject. Our C7/C8 "topic clustering" may partly be a production-batch effect. In a meaningful herbal, each page's plant should drive its vocabulary.

### B5. Binding, quires, page order
- **ReneZ's reconstruction** (summarised by Cuagga, https://www.voynich.ninja/thread-5122.html).
  - Bifolios were produced one at a time: outlines first, then text.
  - The order was disturbed by someone other than the author, then quire numbers were added, then folio numbers, then painting.
  - 12 of the 14 missing folios were lost after foliation.
  - Paint crossing the gutter (f39v → f40r) shows painting was done while the book was disbound.
- **LisaFaginDavis.** The bifolios were probably never meant to nest; Zodiac and Pharma were singulions. kckluge: the Q15/17/19 herbal and pharma sheets share their own A sub-dialect (RZ "Ae").
- **Stolfi.**
  - Q14–19 foldouts came from off-cuts (thread-6071).
  - Quire 10 may be two stitched folios (thread-4938).
  - A later "Retracer" re-inked faded glyphs and details, sometimes wrongly. On f116v he "restored" a flower-offset as an `o`, and the restorations may have turned Voynichese into the Latin-ish marginalia (https://www.voynich.ninja/thread-4740.html, https://www.voynich.ninja/thread-4899.html).
  - Disputed by oshfdk, Koen G and anyasophira, who ask for controls and blind criteria.

### B6. Ink, pigments, imaging
- **McCrone 2009** (https://www.voynich.ninja/thread-2993.html).
  - Ink consistent with 15th-c. iron-gall.
  - Unexplained Cu/Zn, a "titanium compound" and an unknown gum.
  - The ink itself is not dated. Clemens (Beinecke) refuses ink C14 as too destructive and says XRF found no modern elements.
  - Stolfi and asteckley dispute the iron-gall identification (thread-4740).
- **Multispectral imaging.** Easton's 2014 images, including raw 16-bit TIFFs, are now public via ReneZ (thread-570, thread-4364). No palimpsest (davidjackson, thread-744). They help with f1r faded text and the f116v/f17r marginalia, but full-MS imaging is "not happening".
- **Writing speed** (https://www.voynich.ninja/thread-5446.html). dexdex estimates rather than measures: gibberish ~3–4 weeks; enciphering ~one season; faithful copy ~5–6 months. Glyphs are only 1–2 mm (oshfdk, thread-4693).

### B7. Scribes
- **LisaFaginDavis:** 5 hands, diagnosed mainly by the `n` and `k` glyphs. She says multiple scribes make "underlying meaning much more likely" (https://www.voynich.ninja/thread-4951.html).
- **Torsten:** the Archetype data are not public, only 44/225 pages were sampled, two-stroke `k` occurs in Scribe 1, and `n` varies within single folios.
- **Bearing.** If 5 hands share one rule-system and A/B tracks hands, then M requires a *taught*, shared generating procedure. That is possible (quimqu's hand-specific tables, tikonen's "sweat-shop" picture) but costlier. Weakly favours L/C.

---

## C. History and provenance
- **Vellum C14** (https://www.voynich.ninja/thread-3551.html): 1404–1438, from 4 samples pooled, all within 1σ of each other.
  - ReneZ: the calibration slope was lucky, and the 1404–1438 window is roughly one professional lifetime.
  - Anton: pooling assumes one production event.
- **Clothing** (https://www.voynich.ninja/thread-3903.html): Koen dates the Gemini, Virgo and archer dress to 1400–1430, with women's dress narrower still.
  - Mark Knowles argues for the 1430s via Diebold Lauber (Haguenau, 1427–67).
  - The crossbow-armed Sagittarius is unknown before ~1400 and outside the German-speaking area *(snippet)*.
  - R. Sale: red-cheeked "doll" faces match Alsace/Strasbourg (Cod. Pal. germ. 359, dated 1418).
- **Swallowtail merlons** (thread-92, https://www.voynich.ninja/thread-5345.html): treated as a weak northern-Italy clue. The style also occurs in Germany, Switzerland and Austria. Koen G found the only northern manuscript examples are Weltchronik copies, one of which was probably made in Venice.
- **Month names** (https://www.voynich.ninja/thread-4745.html): written by a later hand. "aberil" has been linked to Glarus and Appenzell ("Abrell", 1540) and to Occitan or Catalan.
- **Marginalia, f116v** (thread-4364, Koen G): "so nim gasmich … pox leber" reads as a German recipe or charm ("then take goat's milk… buck's liver"). The marginalia point to an Upper-German milieu.
- **Provenance.**
  - **Rudolf II:**
    - ReneZ's candidate seller is Karl Widemann, from whom Rudolf bought "selzam" books in 1599 for 500 taler (https://www.voynich.ninja/thread-2435.html).
    - The 600 ducats are probably inflated tenfold (Guzy) and not proven to refer to the VMS (thread-2009).
  - **Tepenecz:** the signature on f1r is visible only under UV, and comparisons with his genuine ex-libris are inconclusive (thread-2780).
  - **The Kircher letters:**
    - Baresch's letters to Kircher went via Moretus. Kircher's "Illyrian" remark is disputed (thread-6031).
    - Psillycyber (https://www.voynich.ninja/thread-1428.html) doubts that the 1640 letter refers to the VMS. Kestrel re-reads "Sphynx… schaedata" as "simili modo… schedula".
    - proto57 argues the 1665/6 Marci letter is fake, citing its folds, Latin, and a signature overlay (https://www.voynich.ninja/thread-3137.html). Defenders cite the Kinner letters.
  - **JustAnotherTheory** (thread-6031) doubts the whole chain. Stolfi's answer: the provenance does not affect what the text is, but it does bias "Central European origin" priors.
- **Bearing on L/M/C.** Essentially none, except that a 1404–1438 Upper-German/Alpine milieu sets the language priors for L/C and puts the creation before the Cardan grille. History cannot separate L from M.

---

## D. Bayes-ledger summary
| Evidence | Favors | Rough LR | Confidence |
|---|---|---|---|
| Few corrections; the ones there are add strokes to frequent words and break repeats (Torsten) | M | 1–2 | low (no count, partly snippet) |
| No eye-skip or dittography demonstrated | neutral | ~1 | undetectable without plaintext |
| In-situ layout effects (LAAFU, image-break statistics, text fitted to drawings) | M or C over "L copied from exemplar" | 1.5–2 | medium |
| Bifolio and session habit explains vocabulary class better than subject (z −7 vs −0.7; MDS 1.5%) | M (or a habit-driven script) | ~2, and it confounds our topic evidence | medium–high |
| 5 hands sharing one system; sharp A/B gap on `ed` | L/C over improvised M | ~1.5–2 | medium |
| Line-position profile structured where T&S is flat | against T&S-type M | ~2 vs T&S only | medium; untested vs quimqu |
| Word-specific repetition avoidance not reproduced by the best generator | L | ~2 if confirmed | medium |
| Best generator matches 58/64 measures, including our C9 reduplication | M | lowers C9's value toward 1 | medium–high |
| f88r container label misplaced; zodiac copied from a model | draft→copy workflow (L/C/M all) | ~1 | medium |

---

## TOP 5 for us
1. **Per-word repetition and avoidance dispersion (pre-registerable now on ZL3b).**
   - quimqu's best generator fails exactly here: real common words split into "never self-repeat" (dal, shey, saiin) and "over-repeat" (okaiin 5×).
   - Test the variance of per-type adjacent self-repetition ratios, conditioned on glyph form (to control for the family effect), against T&S, quimqu's scribe, Gaskell & Bowern gibberish, and languages with and without reduplication.
   - Extra dispersion beyond what word form predicts is a **lexical** property, which favours L.
   - This turns our C9 (ratio 1.0, now matched by generators) into a sharper test.
2. **Production-batch vs subject confound.**
   - Partition variance in word class and lexicon by bifolio, by page, and by illustration content (plant identity, section).
   - Re-run C7/C8 (topic clustering) and E055 (labels echo their own page) *within* a bifolio and across the two halves of one sheet.
   - If "topic" vanishes once the bifolio is controlled for, downgrade C7.
   - If the label↔page echo exceeds the same-sheet baseline, that is real L evidence.
3. **Line-position (Feaster 10-slot) profile and image-break behaviour as a generator discriminator.**
   - Compute smooth within-line prefix and suffix gradients and the MarcoP image-break signature (no gallows or q- after a break; lone `s` before it) for the VMS, T&S, quimqu's scribe and Naibbe output.
   - A pre-registered prediction that M-generators produce flat profiles is cheap to test and decisive against T&S-style M.
4. **Build the correction census from Beinecke images and MSI (Easton TIFFs).**
   - Code every stroke addition, scrape and overwrite, then compare the before/after word with local context.
   - Predictions:
     - Copy-error correction (L/C with an exemplar): corrected forms are rare words, and errors look like eye-skips.
     - Cosmetic or anti-repetition editing (M): changes fall on frequent words and break repeats, as in the f75r.P.32 example.
   - Flag Retracer-affected loci (f116v, the dark-ink zodiac labels) and re-run the main statistics without them.
5. **The control nobody ran: fit quimqu's generator to a meaningful text.**
   - Train the same 7-step rule set on a section of a known text (Latin herbal, Moby-Dick re-lined) and count how many of the 64 measures it reproduces.
   - If a meaningless procedure reaches ~58/64 on *meaningful* text too, matching 58/64 says nothing about meaninglessness. Then only failure-mode statistics (items 1 and 3) carry Bayes weight.
   - This calibrates every "generator reproduces X" argument in the M column.
