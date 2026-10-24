# What voynich.ninja knows that bears on our work: synthesis (2026-10-24)

Sources: four research sweeps of https://www.voynich.ninja (about 180 threads), with full reports in
`reports/literature/`. **Access limit:** since about 2025 the forum shows guests only the first post per page of most
threads. Some critiques therefore rest on search snippets, and the reports mark which. Nothing here is a measurement
of ours; nothing moves the ledger until a pre-registered test is run. *(The structure-and-statistics sweep is
pending and will be appended.)*

## 1. Independent confirmations of our results
| Ours | Forum |
|---|---|
| E049–E053: Latin, Romance, Czech/Slavic, Hebrew, Turkish, Romani, abbreviated Latin not found | Forum verdicts agree on every one. DonaldFisk got a "translation" from fake text with the Hauer–Kondrak Hebrew method, the same control our validated attack uses. |
| E053 abbreviated Latin | **Mechanism:** abbreviation *raises* character entropy (h2) (Bowern & Lindemann; Anton), while Voynich needs it much lower. Any abbreviation scheme needs a verbose layer on top. |
| E055: same-label pharma drawings don't look alike | MarcoP (thread-2013): "vaguely similar" at best. Oocephalus (thread-196): labels don't occur on the matched herbal pages. |
| C22 / E056: zodiac labels are not numbers | MarcoP: 263 distinct in 298 labels (ours: 245/292). The "labels are 1–30" proposals (thread-4536) are contradicted. |
| No anchor | **No proposed crib has ever held up:** Bax's names, Bugge's 104 plant names, planet names, and a 2026 dictionary that its own author showed did no better than 500 shuffles. |

## 2. Things that weaken or complicate our findings
1. **C9/C21 (no avoidance of back-to-back repeats) is matched by a new generator.**
   - quimqu's "scribe" (thread-6219, Oct 2026), trained on ZL3b, reproduces 58 of 64 measures, including back-to-back
     repeats at 3.3× chance (real text 3.1×).
   - So C21 cannot by itself separate meaning from a well-built generator. (Our Timm-generator value of 0.76 still
     stands for *that* generator.)
   - **Missing control:** nobody has trained that generator on a *meaningful* text. If it reaches about 58/64 there
     too, matching 58/64 says nothing about meaninglessness.
2. **C7/C8 (topic clustering) may partly be a writing-session effect.**
   - The two halves of one bifolio share e-word habits (z = −7.0); the physically next page does not (z = −0.7)
     (quimqu).
   - Per-page glyph statistics order the pages along a time gradient, and pages of the same bifolio differ by only
     about 2% (npcompl33t, thread-6182).
   - Our topic and label-echo results (C23) must be re-checked with **sheet (bifolio) controlled**.
3. **C3 depends on the glyph grouping.**
   - Our lighter grouping puts Voynich among simple-syllable languages.
   - Koen G's heavier grouping (ch, sh, ain, aiin, ar, al, or, ol, ok, ot, qo, qok…) reaches European values (h2 3.01).
   - The grouping must be fixed *before* the comparison, as we did, and other groupings reported.
4. **C23 needs an absolute rate.** MarcoP found only about 4 of 200 pharma labels (near-)matching their own
   paragraph. Our 1.7× is a ratio, so we should report the raw hit rate too.

## 3. New leads, ranked (for pre-registration)
| # | Test | Why it matters | Cost |
|---|---|---|---|
| 1 | **Per-word self-repetition dispersion.** Do individual words differ in repeating back to back beyond what their form predicts (dal, shey, saiin ≈ never; okaiin 5×)? Compare against generators (Timm, quimqu if obtainable), human gibberish, and languages with and without reduplication. | The best generator fails exactly here. Word-by-word individuality is a **lexical** property, so this is the sharpest meaning test available. | low (ZL3b) |
| 2 | **Session confound:** re-run topic clustering (C7/C8) and label echo (C23) within bifolio, and across the two halves of a sheet | Separates "about the same thing" from "written in the same session" | low |
| 3 | **Score the Naibbe cipher** (public reference ciphertexts and the pykeedy library) on our full battery | A published, falsifiable cipher. Predicted to fail C9, C7 and A/B, which are properties it was not fitted to. | low–medium |
| 4 | **Near-copy mechanism (C12):** do near-copies cluster at a word's *first occurrence* (nomenclator, ReneZ), near their *source on previous lines* (Timm self-citation), or neither (spelling variation)? | Decides between three named mechanisms using data we already have | low |
| 5 | **Vietnamese (tones as a final letter) through the syllabic route** | The only language the forum found matching Voynich's exact repeats. It survives the type-count objection (about 6–7k tonal syllables), and tones-as-suffix could make the closed ending set (C5). | medium (needs a syllable-sign attack) |
| 6 | **pfeaster's Syllabic Hypothesis** (each Voynich word = one syllable of a European text) | Fits C3, C5, C9 and C12. The go/no-go is whether syllabified Latin, Italian or German reaches about 6,000 types per 28.8k tokens | low |
| 7 | **Zodiac:** shed- in masculine vs ched- in feminine signs (MarcoP, 15 tokens, never tested); the o- label gradient; label similarity between neighbouring signs | A gender-linked spelling would be the first text-to-external-fact link | low |
| 8 | **p vs f** (the f57v repeating ring swaps them in one slot), against the claim that p-words follow different rules | Settles sign equivalence, like our r/l and t/k tests | low |
| 9 | **Line-position profiles and drawing-break behaviour** (MarcoP) against generators | Timm-type output is flat, the real text is not. Untested on newer generators. | low |
| 10 | **Constructed-language and glossolalia controls** (Liber Loagaeth, Enochian, Lingua Ignota) on C9, C12, C14 | Meaningful-but-invented text is an untested comparison class | medium (corpora) |
| 11 | **Arabic abjad**, validated attack, words of 4+ glyphs only | The only major medieval candidate not yet searched | medium |
| 12 | **Herbal–pharma matches from the community's rated table** (thread-4067, needs a forum login): do matched pairs share rare glyph groups? (Karlov) | The reverse of E055: drawings against text, with no crib. Locked f102 panels must be excluded. | needs data access |
| 13 | **Correction census** from the Beinecke images and 2014 multispectral images | Corrections on frequent words that break up repeats would point to cosmetic editing (M); copying errors would point to an exemplar (L/C) | high |

## 4. Physical and historical facts worth keeping in mind
- **Text and drawings were made together on the page.** The same frayed pen marks text and picture (pfeaster), and
  words next to a drawing behave differently from ordinary line breaks (MarcoP).
- **No copying error (eye-skip) has ever been shown**, and the corrections have never been counted.
- **Dating:** vellum 1404–1438; clothing 1400–1430/40 with parallels from Haguenau/Alsace; zodiac central figures
  copied from a model (Lauber workshop parallels).
- **Later additions:**
  - The month names are in a later hand, in a peripheral northern French form with Germanic traces.
  - The f116v note reads as a German recipe ("so nim gasmich… pox leber").
  - The writing on f116v has been dated to central Germany.
  - None of these is a usable anchor for the script.
- **Forum lessons we already follow:** run methods on fake text; validate out of sample; translate paragraphs, not
  words; respect positional facts; Zipf and similar statistics are not diagnostic.

## 5. Unverified items (do not rely on them yet)
- A report that Matthew Schwartz (Harvard) argues the text is "iteratively generated gibberish" and that substitution,
  abjad, abbreviation, codebook and Naibbe readings fail on withheld pages in six languages. This was seen only via a
  forum news item.
- "ab aries incipiam" read above a zodiac diagram (Stolfi; thread-4448). It should be checked on the image.
- The claimed "MarcoP reduplication plot" figure: our language sweep's summary contradicts our own measurement and is
  being checked by the structure sweep.
