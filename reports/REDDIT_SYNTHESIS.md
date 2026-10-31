# r/voynich synthesis (Arham, 2026-10-30)

## Source
- **Archive:** r/voynich via the Arctic Shift research archive (Reddit itself and PullPush refused automated access).
  1,933 posts (2011-08 to 2026-10), 1,578 not deleted; 11,037 comments on the 651 posts with 5 or more comments.
  Raw files in `data/external/reddit_voynich/` (gitignored).
- **Readers:** three readers (2011–2021, 2021–2024, 2024–2026) read the whole digest (title, body, top 8 comments per
  post) and flagged each item against E001–E098.
- **Data rules:** no Voynich text from locked folios was copied; Indus material was ignored.

About 85% of posts are untestable speculation or uncontrolled "translations" (many AI-generated). No decipherment claim
used a control text. The useful material comes from a few serious contributors (Ponzi, oshfdk, Gheuens, Zandbergen,
Fincher, the Naibbe author).

## Most promising NEW testable ideas (merged, not ranked by belief)
| # | Idea | Posts | Test | Who could win |
|---|---|---|---|---|
| R1 | Vocabulary drifts with position in the book, not topic (late small-plant pages do not return to herbal words; Naibbe shows no drift) | 1v4hiiz | page similarity vs folio distance, controlling for Currier, section, scribe, sheet; Voynich vs generator, Naibbe, real books | M or L | **Done (E102):** VOID (bands overlap); unscored: no drift in compact sections, like the generator; pharma claim not supported |
| R2 | Rare words are two common words with the space dropped (Zattera slot order fits 95–99% of top types) | 1bxvr5t, 1d74ac3 | share of hapaxes that split into two slot-valid words vs shuffled, languages, generator; could undercut E067 | M or L | **Done (E101):** 31% of once-used words cut into two common words, but the generator does the same and joins in Voynich-like text are undetectable from the words alone; line-end excess is mostly the line-end forms; E067 unaffected (re-spacing 111.9 → 109.1) |
| R3 | Repeated multi-word sequences almost absent (only two 4-word repeats) | w2esca | repeated 3–5-gram counts vs 60 languages, generator, human gibberish | M or L |
| R4 | One word codes one plaintext letter (Trithemius "Ave Maria" type); three-wheel word cipher (Zandbergen arXiv 2104.12548) | eaxi7z, oyeayi, 15gjhdf | simulate, score on E032's 13 features (classes not in E098) | C |
| R5 | Untested published verbose ciphers: Griffoynich (Feaster), Zandbergen's "NOT the Solution", Polygraphia III, Firth's sorting cipher | 1oii3rm, 1q3n62s, 1szxxtg | simulate, 13 features | C |
| R6 | Text squeezed around drawings: words before a drawing gap vs before a normal line end; standalone s before breaks | as5xxr, j1s5ib, 15b1ucr, 1574jxc | a filler process adapts word length; split real words rejoin across the break | M or L |
| R7 | Paragraph-initial gallows are decorative capitals (85% of paragraphs start with one) | slu7jf, 12vrnwm, oyeayi, 1qavl2o | remove the first gallows: does the rest become an ordinary word? (E072-style) | — |
| R8 | Original leaf order (Layfield & Fagin Davis, Digital Medievalist) | 1oik97p, 1x00hs6, 1xfluhl | neighbouring-page vocabulary more continuous in the reconstructed order? (C24) | L |
| R9 | Verse/chant metre | 8c08ay, 80nx9b, hlbndb | regular within-line length vs verse and prose | L |
| R10 | Dice word generator, one die per slot, no copying | czs0g6, iuvmly | a period-plausible M process for the 13-feature battery | M |
| R11 | Vowel harmony with o/a/y as vowels | 4hmqxa | vowel agreement within words; Turkish, Hungarian, Finnish as positive controls | L |
| R12 | Gallows as section markers (t zodiac, f herbal, p pharma) | 1sj3vlq, 1kzhkjt | controlled for paragraph first lines | — |
| R13 | AB and BA word-pair symmetry (Fincher) | 1um5ejs | vs languages, gibberish, generator | M or L | **Done (E104):** GENERATOR-LIKE, M × 3 |
| R14 | Quire 20 as an alphabetical glossary | rl7lgv | are paragraph-first words ordered? glyph order chosen on one half, tested on the other | L |
| R15 | Maltese (not in E049–E063) | pnmh1l | E047/E088 attack with a Maltese Bible | L |
| R16 | f57v inner ring: a 17-glyph sequence repeats 4 times | i6pktp | check in the transcription; ties into the p vs f lead | — |

**New controls and resources mentioned:**
- **Controls:** Enochian (Dee/Kelley); Codex Seraphinianus transliteration (known meaningless); the "hibou" generator;
  Lindemann & Bowern corpus (chirila/Voynich-public).
- **Catalogue texts for E070:** Alchemical Herbal LJS 419, Shénnóng běncǎo jīng, Trotula, Cgm 384.
- **Period cipher and code sources:**
  - Giovanni Fontana's cipher manuscripts;
  - Archevolti's *Arugat ha-Bosem* (Hebrew order-changing codes);
  - Alfonso X's *Astromagia* degree images.
- **Tools and papers:**
  - Hulden's phoneme clustering;
  - Malta 2022 proceedings (CEUR-WS Vol-3313);
  - Timm & Schinner (Cryptologia 2023);
  - Vogt's LAAFU paper.

**Lesson worth recording:** the voynich-toolkit author's Hebrew signal (z 3.6–5.7 against random mappings) was later
retracted by the author as an artefact once fitted-key controls were considered (1r8vw3n, 1s4cco3). This matches
E049/E080.

## Readers' full notes

### Notes A

# r/voynich digest notes, part A (digest_1.md + digest_2.md)

Coverage: digest_1.md read lines 1-4180 in full (451 posts, 2011-08 to 2019-09; last post [d3lcu9]).
digest_2.md read lines 1-3630 in full (190 posts, 2019-09 to 2021-04; last post [mlmqbd]).

Overall: about 85% of posts are link-only, crank decodings with no control, or chat. The useful material is
listed below. Locked-folio rule kept: posts touching f1, f8, f9, f30, f75, f86 (rosette foldout), f102 are
named only; none of their transcription text is copied.

Novelty flags compare against CLAUDE.md (E001-E098).

---------------------------------------------------------------------------------------------------
## 1. Hypotheses about what the text is (mechanism stated)

### NEW
1. **Text written around the drawings: words squeezed or chosen to fit gaps** — [as5xxr] 2019-02-19, [j1s5ib] 2020-09-29
   (the latter concerns locked f75r; text not copied).
   - Statement: words stop exactly at stems and figure limbs. The posters argue that either the writer knew the content
     well enough to plan lengths, or the text is "a jumble of lengths strung together" (M).
   - Evidence: visual only.
   - Testability: good, and M can win it. Using drawing-intrusion marks in the IVTFF (if ZL marks them; otherwise image
     coordinates on DEV pages), compare the length, ending and type of the word just before a drawing gap with the
     word just before a normal line end and with mid-line words. Meaningful text should show only line-end-like
     effects. A filler process would show strong length adaptation (short or truncated words, more one-offs) before
     gaps. Run the same check on illustrated herbals with known text (Culpeper has no drawings; would need a
     transcribed illustrated herbal) and on the generator.
2. **Word stands for one plaintext letter (homophonic word code, Trithemius "Ave Maria" style)** — [eaxi7z]
   2019-12-15.
   - Statement: each plaintext letter has a pool of about 5 code words. A variant has words that encode sums of glyph
     values.
   - Evidence: an argument from the absence of punctuation and from repetition. A commenter identifies the system as
     Trithemius's Ave Maria cipher (early 16th c., later than the vellum).
   - Testability: this class is not among E098's five. Simulate it (Latin or Italian letters → pools of
     Voynich-grammar words) and score it on E032's 13 features plus C21. It predicts a word-bigram structure as rich as
     a letter-bigram structure and about 26 word clusters. NEW.
3. **Verse or chant metre (Kalevala-type trochaic chant; "verse or rhyme")** — [8c08ay] 2018-04-13 (Kven and
   Kalevala metre, from the voynichbirths blog), [80nx9b] 2018-02-27 (Ardic team: "some of the VM is written as
   verse"), [hlbndb] 2020-07-04 (song or chant explains repeats).
   - Testability: E086 found that lines are independent, but nobody has measured line-internal regularity. Count
     glyph-group or syllable-like units per line and per line-half. Compare their spread and periodicity with metrical
     verse (Kalevala, Latin hymns, Psalms) and with prose, controlling for line length set by the page. NEW.
4. **Low-tech random generator (dice, one die per word slot)** — [czs0g6] 2019-09-04 (three dice for prefix, core and
   coda of a syllable), [iuvmly] 2020-09-18 (7-sided dice; the poster's tables are wrong, as a commenter shows).
   - Testability: a period-feasible M process with no human memory, distinct from Timm & Schinner's copy-modify.
     Build it from E074's front/middle/ending kit, with slot probabilities only and no copying. Score it on the
     13-feature battery and C21. Prediction: it fails near-copies and the vocabulary-richness pattern. PARTLY related to
     E093's process ladder (P1-P4); the dice version proper is NEW.
5. **Vowel harmony (Cuman or Turkic claim)** — [4hmqxa] 2016-05-03, quoting rationalconspiracy.com ("vowel harmony,
   which several have observed in the Voynich glyphs"); also [9rj7nh] comments (Manchu and Turkish reduplicate).
   - Testability: take the vowel candidates from Sukhotin (Guy 1991: EVA o, a, y; [ejbzml], [cquesz] comments). Test
     whether the vowel classes within a word agree beyond chance. Use Turkish, Hungarian, Finnish and Uyghur as
     positive controls, Latin, Italian and Hebrew as negatives, and the generator as M. The Turkish letter attack is
     done (E049), but this structural test is NEW.
6. **Paragraph "theme words": a repeated nucleus with particles inserted, changing per paragraph** — [lqz0p4]
   2021-02-24; also [cxfm2w] and [d026m9] ("babble passages", words repeated with one letter different).
   - Testability: measure whether near-copy families are concentrated within paragraphs more than within lines or
     pages, controlling for sheet (C24). This is the open "where near-copies come from" lead in CLAUDE.md §6.3.
     PARTLY (E058, E066 family-level).
7. **Abugida with implied vowels (Banasik's Manchu)** — [wv1t3] 2012-07-20, [201rjs] 2014-03-10, [3kpjdo] 2015-09-12.
   - Mechanism: Manchu in a modified script, with "a" and "e" implied. The poster ran Glen Claston's v101 transcription
     through a converter. Claims "hundreds of word matches", with no control. Lisp code exists (wporquet).
   - Testability: Manchu is not in the searched list. A Manchu Bible (19th-c. translation) might be obtainable. The
     E063/E087 pipeline with vowels stripped would test it. NEW language; low prior.
8. **Candidate languages not in the searched list**, all with no evidence beyond assertion:
   - Knaanic, or Judeo-Czech ([ejbzml] comment 2020-01-03);
   - Cuman, via Codex Cumanicus ([hlbndb], [4hmqxa]);
   - Basque ([gxldma]);
   - Kven/Finnic ([8c08ay]);
   - Galwegian ([ml9st4]);
   - Avestan ([7o788a]);
   - Old Uyghur script ([7tug1l]; Uyghur language done in E063);
   - Tocharian ([dysuzv]);
   - Albanian ([56k1le]).

   Only Cuman (Codex Cumanicus) and Basque have usable corpora. NEW but weak.

### PARTLY TESTED
9. **Constructed or sect language: Balaibalan** — [9scmlc] 2018-10-29.
   - A commenter notes it is late 16th c. and known only from a dictionary.
   - **Dee/Kelley Enochian**: [ephmhy] 2020-01-16 shows the Angelic languages fit Zipf as well as Voynichese does
     (corpora about 4,500 and 1,100 words, from Laycock's *Complete Enochian Dictionary*).
   - Matches the queued "constructed-language controls" (CLAUDE.md §6.5). Enochian is obtainable; Balaibalan is
     dictionary-only.
10. **Genuine meaningless text as an artistic or magic prop, glossolalia or automatic writing** — [d026m9],
    [ghct6z], [8v59tv] ("lorem ipsum", MinaLima prop-book makers), [ehrbvm] (wants a glossolalia corpus). PARTLY
    (E045, E067, E068 human gibberish). A transcribed glossolalia corpus would be a new M control.
11. **Copy of a lost text by a copyist who could not read it** — [1jskz0] 2013-08-06, [7ln5tb], [e1w3tb]. Commenters'
    rebuttal: a copyist would reproduce a recognisable script. Not directly testable; partly covered by the
    "no language matches like itself" result (E079).
12. **Nomenclator or word-list obfuscation (gibberish words keyed to a separate dictionary)** — [jd73zk] 2020-10-18.
    ALREADY TESTED: E098 nomenclator CLASS FAILS.
13. **Verbose cipher, nulls, cipher disk** — [e45equ] 2019-11-30 (cites D'Imperio §4.4.2 and §9.2, Pelling, Julian
    Bunn), [e1hs3w]. ALREADY TESTED: E062 and E098 (null words, rotating tables). Commenters correctly note that
    polyalphabetic ciphers flatten glyph frequencies, which Voynich does not.
14. **Anagrammed or sorted-letter Hebrew (Hauer & Kondrak 2016/2018)** — [7sq3t7], [a1tlv4], [7ti6ac], [d7hz91].
    ALREADY TESTED: E049, E080-E084, and E098 (in-word sorting PARTIAL). Their ranking put Hebrew first, Esperanto
    second, Mozarabic and Mazatec high, Italian 8th.
15. **Each glyph = an abbreviated Latin word or syllable** — Gibbs [6ynbi1] 2017-09-07; Weiler [gftuav]/[ggxxx4]/[gi8zle]/[glc5ni]
    2020-05 (Frederick III notebook cipher plus Cappelli abbreviations); [d026m9] (Latin without vowels, similar
    sounds merged).
    - ALREADY TESTED: E053 and E071 (L-abbrev).
    - Community rebuttal: Zandbergen's conditional character entropy is far too low for abbreviation-dense text.
      Marco Ponzi shows one EVA word reading as 10 different Latin words under Weiler's rules.
16. **Proto-Romance / "Ischia" language (Cheshire 2019)** — [aj3via], [bouxnm], [bpaedd], [bpfuby], [bsbmpa],
    [jkjomc]. Romance languages searched (E049-E063). No control; Bristol withdrew its press release.
17. **Romani in a modified Syriac script (Bax 2014, Derek "Volder Z" Vogt)** — [1yem2l], [4wy39b], [7hn996],
    [cquesz], [ev9h5v], [hqcq07]. Romani searched (E049-E052).
    - [cquesz] 2019-08-15 did a useful mini-test: Vogt's sound values on the five f77r "element" labels do not match
      Romani (romlex) words for air, water, fire or earth.
    - Bax's anchors: "Taurus" read as a constellation label in the f68r region; a juniper-like word.
18. **Turkic (Ardıç family, Calgary 2018)** — [80nx9b], [a6b90b], [aba2n4], [extgup], [gop5fz], [kju860]. Turkish
    searched (E049). Their paper was rejected by peer review; a Turkish-speaking commenter calls the derivations
    far-fetched.
19. **Hebrew via Strong's roots, phonetic "defective" spelling** (Yokubinas: [92ewog], [9rc87c], [ad0lqr], [ar2yy7],
    [eiagei], [hvep6b] and many more); **Rainer Hannig's Ashkenazi Hebrew 2020** ([hb41b7]). ALREADY TESTED (Hebrew
    campaign E080-E084). [adu8fg] (Marco Ponzi) dissects the four-step method that makes these readings arbitrary.
20. **Nahuatl / New World (Tucker & Talbert 2014, 2017-2018)** — [1vt8nt], [1wy668], [6g3sj6], [4vltz6], [5ooxct],
    [9dojvy], [fwl527], [7suqfd]. Rebuttal: the vellum is dated 1404-1438. PARTLY: E079 skeleton traits put Nahuatl
    nearest (1.74) but outside the same-language band. No letter attack on Nahuatl is listed in CLAUDE.md.
21. **Other assorted one-person decodings with no control and no method** (listed only so they are not re-read):
    - Italian Morse code (O'Neil): [cyx5cl], [d4i96t], [d6tzmh]; [d6ybqe] reproduces it and shows it is arbitrary;
    - Serbo-Croatian (A. L. Morris): [d48uon], [d61siq];
    - Persian: [lgcrf8], [ljpu94], [lst30e];
    - Landa Khojki: [24rndu];
    - Slovene: [lgitn4];
    - Middle English gematria: [83dgmy];
    - Vigenère to French: [a2isi9];
    - Playfair: [cqtsmm];
    - Galwegian / Templar: [mko50f], [ml9st4].

---------------------------------------------------------------------------------------------------
## 2. Measured or checkable facts

### NEW (to the project's fact list)
1. **f57v inner ring: a 17-glyph sequence repeated exactly 4 times** — [i6pktp] 2020-08-09. Known on the forums. It is
   checkable directly in the ZL IVTFF for f57v (a DEV page). Relevant to the queued "p vs f (f57v ring)" lead. It is a
   candidate "key-like" or alphabet-like sequence.
2. **Exact back-to-back word repetition counts** — [9rj7nh] 2018-10-26 and [a1tlv4] (Marco Ponzi).
   - Over 250 doubles and about 10 triples (runs of 3-4).
   - Picatrix (Latin, about 3× longer) has 15 exact repeats; Voynich has 292.
   - Repeats are spread across pages rather than clustered as incantations would be.
   - Taiwanese uses systematic triple reduplication (Shang Guowen PhD thesis).
   - The doubles are ALREADY covered by C21/E043/E064. The **triple-run rate** and the **evenness of repeats across
     pages** are NEW statistics, testable against languages, incantation genres and the generator.
3. **Words adjacent to drawings fit around them** — [as5xxr], [j1s5ib]; see Hypothesis 1.
4. **First word, or first five words, of each page are unusually unique** — [1ub5gb] 2014-01-03, [1vrv3v]
   2014-01-21 (esotericprogramming.info). PARTLY known: paragraph-initial gallows; E075 line-start pieces; label
   step 0. A page-initial-word test controlling for gallows is cheap.
5. **Glyph positional variants are normal in period Latin hands** — [eipgcz] 2020-01-01 (St Gall 942: two shapes of s
   by position). [ejbzml] 2020-01-03: EVA n and i in complementary distribution (n word-final); medial n should split
   words. PARTLY (E059/E092 glyph-cut work).

### PARTLY / ALREADY TESTED
6. **Interchangeable endings or/ol/y in the botanical section; top-100 word list for the herbal section** —
   [7c7muc] 2017-11-11. ALREADY (E059: r ≠ l; ending classes).
7. **Character entropy is an outlier at glyph level, typical at word level** — Lindemann & Bowern 2020 [jq8q6u],
   [io4fx0]. ALREADY (C: glyph predictability below all alphabets).
8. **About 2,400 spaces are uncertain in transcription (Zandbergen & Landini)** — [cf7hka] 2019-07-19. PARTLY (E086,
   E092).
9. **Five scribes (Lisa Fagin Davis 2020)** — [f677q6], [gf9en2], [fvg0p8]. ALREADY in measured facts.
10. **Corrections do exist; the "no errors" claim is false** — [4shjhk] (f1r retouching, locked page, no text copied),
    [cxfm2w], [ghct6z], [dj168r]. No count is given. A correction census is already on the project's "bigger work"
    list.
11. **Codicology and dating**:
    - Parchment not a palimpsest (multispectral imaging by Paula Zyats, Yale) — [a324az], [dyg8bd], [d0oiu0];
    - McCrone: ink applied shortly after the parchment was made — [a324az];
    - Touwaide (2016, 2019): calf parchment; "almost certainly not a medical herbal" — [evsids] 2020-01-29;
    - f116v multispectral images — [5e3fs6];
    - the f1r Tepenec ex-libris is visible fully only in multispectral images — [egxk9e], [hgndp9] (locked page,
      mentioned only);
    - quire signatures — [e1x8vg];
    - month names in Occitan or northern French (Zandbergen) — [7z0mdm], [jc8441];
    - f4r stem annotation "rot" (German for red), a colour note, with a parallel in Vicenza Bertoliana ms 362
      (Zandbergen 2012, Touwaide 2016) — [aoz9y9] 2019-02-10;
    - f66r German phrase "den muss der"; f17r, f66r and f116v carry Latin and Voynichese together; f49v has a margin
      column of numerals 1-5 beside glyphs — [cqbfis] 2019-08-14;
    - f1r right margin has an a-b-c-d letter column, an alphabet attempt (locked page, mentioned only) — [isog8t],
      [glb6rz].
12. **Zodiac nymph counts (29-30; 15+15 on the doubled signs) read as days or degrees** — [itwqgx], [jc8441].
    ALREADY (E094: figures = degrees).

---------------------------------------------------------------------------------------------------
## 3. Decipherment claims (method; control used?)

None of the roughly 40 claims in these two files used a control text, a blind replication or a whole-text
prediction. Community rebuttals that are themselves useful as method:
- **[adu8fg] 2019-01-08 (Marco Ponzi)**: the "four steps" decomposition of arbitrary decodings: a free transcription
  table, a dictionary search for similar words, free choice among senses, free reordering. This is a good checklist
  for the project's own claim rules (already enforced by rule 7).
- **[ar2yy7] 2019-02-15**: proposes a blind replication protocol (two people decode an unseen page independently and
  compare). It matches the project's "known answers first" rule. Note E094's lesson: AI sub-agents cannot be blind
  judges.
- **[9epbzv] 2018-09-10**: replicability criteria; warning signs (multiple languages, nulls at will, Google Translate).
- **[edgem9] 2019-12-20**: proposed solution threshold: map at least 80% of non-unique words with a fixed character
  mapping and a limited rule set. The poster also says a character swap reached 20% of the corpus and still produced
  gibberish.
- **[d6ybqe] 2019-09-20**: a commenter reran O'Neil's Morse anagram code and produced equally "fluent" alternative
  Italian. This is a worked example of a null control.
- **[glc5ni] 2020-05-17**: one EVA word reads as 10 different Latin words under Weiler's rules.
- **[jwnciz] 2020-11-18**: Google language-ID labels an FSG transliteration as "Hindi". A naive idea; not useful
  without controls.

One claim with a slightly better design:
- **[j28hp4] 2020-09-29**: searched for words that co-occur with illustration features (flower pages, blue paint,
  spots) and proposed words for "flower", "blue" and "spot" (academia.edu, "Voynich Pattern Searching and Statistical
  Analysis"). There was no permutation null and no sheet control. Commenters note the paint may be later.
  - **NEW testable**: a pre-registered word ↔ drawing-feature association with a max-T permutation test, a held-out
    half and sheet blocking.
  - Use features coded on DEV herbal images: flower present, root type, leaf shape. Paint colour is weak because
    colouring may be later; CLAUDE.md already notes pharma colours cannot test colour.
  - E085 (same-plant pages share words: NO LINK) and E055/E060 are PARTLY related.

---------------------------------------------------------------------------------------------------
## 4. Tools, datasets, papers, researchers we may lack

### Datasets and corpora (most useful first)
- **Lindemann & Bowern corpus for the entropy paper**: github.com/chirila/Voynich-public ([jq8q6u] 2020-11-08). A
  large set of modern and historical texts already prepared for character-entropy comparison.
- **Enochian (Dee/Kelley) corpus**: in Laycock, *The Complete Enochian Dictionary* ([ephmhy]). For the
  constructed-language controls.
- **Giovanni Fontana's two 15th-c. cipher manuscripts** (Bellicorum instrumentorum liber; BSB Munich, digitised) and
  Philip Neal's page philipneal.net/voynichsources/fontana_cipher_manuscripts/ ([dokuqc], [e1hs3w], [cv6kuy]). The
  only known long 15th-c. cipher books. A natural period known-answer cipher class for E098-type batteries.
- **Archevolti, *Arugat ha-Bosem* (1602), chapter on encoding methods** (ResearchGate 274333150; [92gtjz]
  2018-07-27). Period Hebrew concealment methods, which fill the "boundary/order-changing codes" gap in the Hebrew
  campaign.
- **Alfonso X *Astromagia* (BAV Reg. Lat. 1283a) and *Lapidario*; Fendulus; *Astrolabium planum* (Pietro d'Abano)**:
  360 degree-images (moirogenesis / paranatellonta). Panofsky and Salomon compared the Voynich zodiac layout to
  *Astromagia* ([dd4zj2] 2019-10-04, [iqsg7e]). E096 used Lilly and al-Biruni tables; this is a different period
  table that could get the same pre-registered treatment (PARTLY E096).
- **Codex Cumanicus** (Cuman / Kipchak glossary, Venice Marciana) ([hlbndb]). Short; better as a wordlist than as a
  corpus.
- **Aramaic incantation bowls (Montgomery 1913)** ([hlbndb], [hvep6b]). An incantation-genre repetition control for
  C21.
- **Picatrix (Latin)**: the exact-repeat comparison above ([a1tlv4]).
- **Glossolalia transcripts**: wanted but not found by [ehrbvm]. A possible new M control if any exist.
- **Taiwanese triple-reduplication thesis (Shang Guowen)**: core.ac.uk/download/pdf/48645452.pdf ([9rj7nh]).

### Generators and M-side papers
- Rugg & Taylor, "Hoaxing statistical features of the Voynich Manuscript", *Cryptologia* 2016 ([6ld8eq]).
- "hibou" meaningless-text generator, web.onetel.com/~hibou ("21st Century Voynich Manuscript"; [7c7muc],
  [7sq3t7]). An older, independent M generator.
- Wentian Li 1992, "Random texts exhibit Zipf's-law-like word frequency distribution" ([ehrbvm]).
- Timm & Schinner 2019 (TTAS.pdf): already in use.

### Linguistic and statistical papers
- Bowern & Lindemann, "The Linguistics of the Voynich Manuscript" (lingbuzz 005415), and Lindemann & Bowern,
  "Character Entropy..." (lingbuzz 005522 / arXiv 2010.14697) ([io4fx0], [jq8q6u]).
- Montemurro & Zanette 2013, keywords and co-occurrence (PLOS ONE) ([4qexkz]); Amancio et al. 2013 (PLOS ONE)
  ([4q2nxu]).
- Jacques Guy 1991, "Statistical properties of two folios" (Sukhotin vowels o/a/y; EVA ch ≈ Visigothic/Beneventan t)
  ([aw38i4]).
- Reddy & Knight 2011, "What we know about the Voynich Manuscript"; Knight et al. 2011, Copiale ([atka6q]).
- Keldysh Institute preprint 2016-52, statistical regularity of European languages ([4xtbrb]); arXiv 1604.04149,
  coding/decoding methods ([4ijcid]).
- "The Voynich Manuscript: Symbol roles revisited" (ResearchGate 348012391; ligatures) ([m3snig]).
- Emma May Smith (agnosticvoynich): line-first transformation ([5chk8h]), word position in Q20 ([5p4dfu]), k/t
  distribution ([6abyo0]), bench gallows ([6d1cnp]), glyph combinations across word breaks ([bz91n9]); also the
  Smith-Ponzi refinement of Stolfi's word grammar ([cf7hka]). Mostly ALREADY covered by E059, E075 and E086.
- Marco Ponzi, part-of-speech tagging of Voynichese (medium.com/viridisgreen) ([am0wnp], [lf7usg]). Possibly useful
  for E093-style structure work.
- NSA declassified material (D'Imperio 1978; Currier; Friedman) ([c3hsak], [e45equ]).
- Ewa Śnieżyńska-Stolot (2001): German traits of the zodiac medallions ([iqsg7e]).
- Beinecke/Yale facsimile essays (Zandbergen, Hunt, Zyats et al. on physical findings, Sherman, Rampling, Clemens)
  ([iqsg7e]).

### Tools
- voynichese.com (searchable EVA); jasondavies.com/voynich (viewer); inversed.ru MDS and conditional-character plots
  ([3vf63a], [5k5hs1]); kulibali.github.io/enochian (automated application of Vogt's phonetics) ([cquesz]);
  github.com/ambertide/VoynichExplorer (transcript parsers) ([mkjx8k]); Landini-Stolfi interlinear file ([lc98xy]);
  wporquet Lisp Manchu converter ([3kpjdo]).
- Zandbergen's proposal for "hand statistics": record the coordinates, size and slant of every glyph ([aoz9y9]). Not a
  dataset that exists; noted as an idea for a correction or scribe census.

---------------------------------------------------------------------------------------------------
## 5. Image identifications with some evidence

None of these is strong. Most are single-person look-alikes.
- **f33v sunflower and capsicum** (Hugh O'Neill, *Science* 1944/45; [6cm8ou], [a324az]): disputed. A commenter says
  the f33v root structure is wrong for *Helianthus* ([d4ders]).
- **Twinflower (*Linnaea*) on f10v; goat's beard (*Geropogon*) on f7r**: [cv6kuy] 2019-08-25, side-by-side images.
- **Star anise (*Illicium verum*) on f16v**: a Finnish biologist via Bax; [czgdho] 2019-09-04.
- **Heartsease (*Viola tricolor*)**: a commenter in [f09z3p] (the post concerns a locked folio in the f9 range; noted
  only).
- **White water lily on f2v** ([afnjbm]); **juniper** (Bax) ([ebjnn1]); **f4r**: oregano or fennel guesses, but the
  "rot" note is the solid fact ([aoz9y9]).
- **Pangolin or armadillo on f80v**: [1wy668], [7uzkd8]. Look-alike only.
- **Opuntia, Passiflora and other New World plants** (Tucker & Talbert): [1vt8nt], with a botanist commenter's
  rebuttal ([1vt8nt] comments).
- **Pisces/Cancer artwork parallels with MS Ludwig XII 8 (Getty, c.1464, Michael Haintzmann of Babenhausen)**:
  Cancer as a lobster in both ([ejof23] 2020-01-04). A checkable art-historical parallel.
- **Zodiac layout like Alfonso X's *Astromagia* degree images** (Panofsky, Salomon): [dd4zj2], [iqsg7e]. The best
  supported item here.
- **f68r possibly showing an eclipse of 1409** (Bax site) ([5wfzxf]); **f57v "5"-like sign is a pilcrow** ([aoojs7]
  reply, stephenbax.net/?p=1972); **f77r labels as the four or five elements** ([cquesz]); **f116v compared with
  medieval charms** (David Jackson) ([381v7v]); **Q13 nymphs compared with an unusual group of psalters**
  ([6he7xb]); **Tuscan Herbal 3-a, Trinity College herbal and bestiary comparisons** (voynichimagery) ([4m0ohl],
  [69l0ze]).

### Notes B

# r/voynich digests 3 and 4: notes for the research project

Both files were read in full: digest_3.md (259 posts, 2021-04-07 to 2022-12-09; last post id **zggyi5**) and digest_4.md (252 posts, 2022-12-17 to 2024-10-21; last post id **1g8xh1u**).

Overall, about 85% of posts are low-value: self-declared translations with no method, plant look-alikes, AI chatbot output, and Templar, alien, demon or Oak Island stories. The useful material comes mostly from a few serious commenters (Marc_Op / Marco Ponzi, ptr47, oshfdk, Koen Gheuens, Rene Zandbergen), whose posts are cited below.

Locked folios (f1, f8, f9, f30, f35, f38, f51, f52, f56, f75, f86, f87, f102, f105, f114) are named where a post concerns them, but none of their text is copied. To be safe, no EVA strings are copied at all.

Novelty flags are judged against CLAUDE.md sections 3, 5, 6 and 8 only. I did not open other project files, so any item flagged "verify" needs a check against E063's language list or FORUM_SYNTHESIS.md.

---

## 1. Hypotheses about what the text is (mechanism stated)

### NEW

**1.1 "Rare words are two common words written without a space" (Zattera slot order)**
- **Posts:** 1bxvr5t (2024-04-07, comment); 1d74ac3 (2024-06-03, comment); 1g3tgmc (2024-10-14, the "Roman-numeral-like rigid order" variant).
- **Claim:** Glyphs in nearly all high-frequency words follow one fixed slot sequence (Massimiliano Zattera's "slot alphabet"). Words that break the order can usually be split into two words that do follow it. On this view, spaces were dropped to make new, rarer words.
- **Evidence offered:** 95% of the 180 commonest words and 99% of the top 100 fit the slot order. No controls.
- **Test:**
  - Fit a slot grammar on common DEV word types using one half of the book.
  - On the other half, measure the share of hapax and rare types that split into two slot-conforming common types. Compare with:
    - pseudo-hapaxes made by shuffling glyphs within slots;
    - the same split test on 8–10 languages (do rare Latin or Turkish words split into two common words?);
    - the Timm generator and Gaskell–Bowern gibberish.
- **Why it matters:** If true, it bears directly on the 69% hapax rate and on E067's vocabulary-richness result (M × 3). The richness could be an artefact of joined pairs.
- **Novelty:** NEW. The joined-pair test has not been run. Related: E074 (front + middle + ending pieces), E086/E092 (spaces are mechanical; this depends on the transcription), E087 (spaceless attack).

**1.2 "Each Voynich word encodes a fixed-length chunk of plaintext through three wheels or tables" (Cardan-grille / wheel cipher)**
- **Posts:** oyeayi (2021-08-05); 15gjhdf (2023-08-02, a "Voynich Cipher Disk" paper on ResearchGate); w2esca (2022-07-19, comments); 1fz3dwn (2024-10-08, comment: "Zandbergen's system addresses the low entropy").
- **Mechanism:** Split the plaintext into trigrams, ignoring plaintext spaces. Write each trigram as prefix + core + suffix, each taken from its own wheel or column, with frequent fragments assigned to frequent letters. Based on Zandbergen, "The Cardan grille approach to the Voynich MS taken to the next level", arXiv 2104.12548.
- **Evidence offered:** Marco Ponzi's working implementation. Only about 20% of the words it produces from English text occur in the Voynich manuscript. The ResearchGate disk paper is unconvincing: its "translations" go through Google Translate.
- **Test:** Because word boundaries carry no plaintext boundary, the end slot of word *i* should predict the front slot of word *i+1* about as strongly as plaintext letter bigrams predict each other. This is a junction prediction.
  - It fits the known q- after -y junction (E059) and E075's 79% consistent neighbour shifts.
  - Build synthetic books (Latin and Italian, wheels frequency-matched), then run E032's 13 features plus the E059/E075 junction measures. This is a known-answers-first check: does the class reproduce the Voynich profile?
- **Novelty:** NEW as a class. E098 tested nomenclators, in-word rearrangement, null words, rotating tables and abbreviation + cipher; E062 tested verbose ciphers with one table per scribe. It may overlap E098's "rotating tables", so check E098's definitions.

**1.3 "Paragraph-initial gallows are decorative capitals, not part of the word"**
- **Posts:**
  - slu7jf (2022-02-06): *Tractatus novus de astronomia*, Spain, 1400–1450, shows red capitals, blank spaces left for capitals never painted, and a gallows-like abbreviation sign;
  - ss7jhl (2022-02-14): character comparison;
  - 12vrnwm (2023-04-23): drop caps and indentation on f1r (locked; text not copied);
  - 1ds1hx3 (2024-06-30): the red "weirdos" on f1r;
  - oyeayi (comment): Bowern & Lindemann 2020 report that 85% of paragraphs begin with t, k, f or p ("Grove words": unusual words at the start of paragraphs).
- **Test:**
  - Strip the first gallows glyph from paragraph-initial words.
  - Check whether the remainders match ordinary line-internal vocabulary at the rate that frequency-matched line-internal words do.
  - Compare with Latin texts where the first letter is a capital: removing it should give a known word.
  - Compare with the generator.
- **Novelty:** NEW. E072 tested whether ot/ok detaches as a front piece. The paragraph-initial gallows has not been tested in CLAUDE.md.

**1.4 "Quire 20 is a glossary or alphabetical list"**
- **Post:** rl7lgv (2021-12-21).
- **Evidence offered:** Short paragraphs, frequent mid-line endings, similar paragraph-first words, no overall topic. The poster noted that "if alphabetical, they were sloppy".
- **Test:**
  - Choose a glyph order on half of the Q20 paragraphs.
  - On the other half, measure how sorted the paragraph-first words are (for example, the longest increasing subsequence), against permutations within sheets (C24).
  - Run the same procedure on a real alphabetical glossary (for example Alphita or the Sinonoma Bartholomei) as a power control, and on a non-glossary herbal.
- **Novelty:** NEW.

**1.5 Maltese as the underlying language**
- **Posts:** pnmh1l (2021-09-13); te0yrk (2022-03-14, comment).
- **Argument:**
  - Maltese is Semitic, so its word lengths are closer to Voynich than most western languages are.
  - Its consonant inventory is reduced enough to fit the Voynich sign count.
  - It belonged to the Latin cultural sphere.
  - It had no standard written form c. 1400; Il-Kantilena (1470s) is irregular.
- **Rebuttal:** One commenter reports that Prof. J. Brincat saw "no resemblance". That is an opinion, not a test.
- **Test:** Run the E047 validated attack on A and B, plus the E088 spaceless form, with a Maltese Bible (check eBible for mlt).
- **Novelty:** NEW; Maltese is not listed in E049–E063 (verify). This is the only new candidate language here with a usable corpus. Others mentioned:
  - Knaanic / Judeo-Czech (1fqs73m, 2024-09-27): no usable corpus;
  - Basque (1fksnnp, 1fkzhlj, 1fmd64i, 2024-09): verify against E063;
  - Pahlavi-style heterographic writing, i.e. Persian written with Aramaic word-spellings (1d33uau, 2024-05-29, citing Hermann, arXiv 1709.01634): NEW idea, hard to test, low prior. Judeo-Persian is on the Hebrew campaign's untested list.

**1.6 "Words get shorter, or become fragments, where the text squeezes around drawings"**
- **Post:** 15b1ucr (2023-07-27).
- **Examples given:** f2r, f26r, f29v, f36r, f47v, f90v, f93v.
- **Interpretations:**
  - The poster: this makes gibberish more likely.
  - Marco Ponzi: Trinity O.2.48 and the Vermont Herbal do the same thing, using abbreviated words or one word broken into pieces.
- **Test:** In IVTFF, lines interrupted by a drawing are marked. Compare word length and word completeness in short or interrupted segments with full lines, controlling for line position (E059). Then test the two readings:
  - **Meaningful-scribe reading:** fragments are prefixes or suffixes of common words, and the two sides of a break rejoin into a known word more often than chance. E071's truncation method can be reused.
  - **Generator reading:** complete short words fill the gap.
- **Novelty:** NEW.

**1.7 Friedman's a-priori (taxonomic) artificial language**
- **Posts:** pnwwq0 (2021-09-14); q6sr0j (2021-10-12); te0yrk (2022, comment correcting a poster: Friedman said *a priori*, not *a posteriori*); ucinry (2022-04-26: Lingua Ignota, plus a Zipf comparison of Dee's two "angelic" languages in older post ephmhy).
- **Mechanism:** Word pieces stand for semantic classes, as in Wilkins' philosophical language.
- **Prediction:** Pieces should cluster by illustration class, and the same plant should share pieces.
- **Novelty:** PARTLY TESTED. E054 (topics) was VOID; E085 found no shared words between same-plant pages; E072/E074/E078 covered pieces. Constructed-language controls (Enochian, Lingua Ignota) are queued in CLAUDE.md §6 item 5.

### PARTLY TESTED / ALREADY TESTED

**1.8 Self-citation: copying from the line above** — PARTLY TESTED.
- **Posts:** 188as16 (2023-12-01: after removing repeated characters, words look copied from the line above or two lines above); xm5db4 (2022-09-23: Timm & Schinner video, with code at github TorstenTimm/SelfCitationTextgenerator); 15h6mlz (2023-08-03: Timm & Schinner, Cryptologia 2023, "discussion of text creation hypotheses").
- **Test:** Measure the distance and direction to each word's nearest near-copy (vertical, same horizontal position, versus preceding words on the same line), controlling for sheet.
- **Status:** E032/E064 tested the generator. "Where near-copies come from" is queued in §6 item 3. The vertical same-column prediction is the specific new angle.

**1.9 Javanais-type infix steganography** — PARTLY TESTED.
- **Post:** olcbfx (2021-07-16). The mechanism is a fixed syllable inserted after each consonant.
- **Rebuttal in thread:** That would make words longer than they are.
- **Status:** E061 (stems vs padding) was VOID; E098 tested null words.

**1.10 Syllable at the start of each word, followed by "distractor" closing glyphs, with plaintext words spanning lines** — PARTLY TESTED.
- **Post:** 1c9pwcf (2024-04-21).
- **Status:** E061 and E098 (nulls). E086 found lines independent, which goes against words spanning lines.

**1.11 Anagram / in-word sorting** — ALREADY TESTED (E098, in-word sorting PARTIAL).
- **Post:** 1ck95e0 (2024-05-04).
- **Claim:** First-order entropy is close to Hebrew, while second-order entropy is very low.

**1.12 Verbose cipher, or an encoding of a logographic language** — PARTLY TESTED.
- **Posts:** thibpl (2022-03-18: Chinese characters encoded by components as digraphs and trigraphs; cites Pelling, Gheuens' "entropy hunting", Bunn's verbose homophonic cipher, Zandbergen's sol_ent page); mt18bu (2021-04-17), tjlkub (2022-03-21) and utrcne (2022-05-20): Stolfi's symmetric (binomial) word-length distribution was read as East-Asian-like.
- **Status:** E062 and E098 (nomenclator); E065 syllable route NO GO; E044 not syllable spacing.

**1.13 Verbose cipher plus an abbreviation system** — ALREADY TESTED (E098, abbreviation + cipher class fails).
- **Post:** umy240 (2022-05-11).

**1.14 Genre or verse lowers entropy** — PARTLY TESTED.
- **Posts:** 1fmd64i (2024-09-21: scientific, chant and legal texts as lower-entropy genres); 1fmjnf9 (2024-09-22: epic verse, type/token ratio of Homer).
- **Status:** E033/E034 (genres) and E090 (out-of-genre power).

**1.15 Chants, prayers or spells explain the repetitions** — PARTLY TESTED.
- **Posts:** nzfqpo (2021-06-14, about f75r, which is locked); 1fzh43u (2024-10-09, about f58v).
- **Counter-argument (Marco):** Chants repeat identical words; Voynich repeats near-identical words.
- **Status:** C21; E043/E046; E033 included hymns and Psalms.

**1.16 Glossolalia, or human spontaneous gibberish** — ALREADY TESTED (E045, E067 M × 3, E068 M × 1/3).
- **Posts:** 1d74ac3 (2024-06-03: Fasano, "The Voynich Manuscript: A Non-Stochastic…", semanticsarchive.net, on glossolalia; criticised for tiny samples); Gaskell & Bowern 2022 (CEUR Vol-3313 paper4, already in project data).

**1.17 Abbreviated Latin** — ALREADY TESTED (E053, E071).
- **Posts:** my148e and nopt5a (2021: Domingo Delgado); t90sn4 (2022).
- **Note:** Zandbergen's statistical argument against abbreviation is in the lower half of voynich.nu/extra/sol_ent.html: abbreviation raises entropy, while Voynich entropy is low.

**1.18 Women's medicine / "women's secrets" enciphered, author Johannes Hartlieb** — not testable by text statistics.
- **Posts:** 14ssbk6 (2023-07-07); 1c5znj9 (2024-04-17); 1d92wwr (2024-06-05); 1eiayzm (Brewer & Lewis, *Social History of Medicine*, 2024-03-22).
- **Evidence:** Hartlieb's herbal and his onomancy wheel diagrams.
- **Comment in thread:** The manuscript has several scribes and the painting was added later, which weakens the case for a single author.
- **Status:** No factor possible. Could inform the choice of topic cribs.

**1.19 Quire 13 as plant physiology** — not testable by text.
- **Posts:** 1fknklg (2024-09-19); Taiz & Taiz 2011, *Chronica Horticulturae* 51(2) p. 19.

**1.20 Speculation with no testable mechanism** — not testable. Music cipher (1d8o7ps, 1fb77g8), humoral diagrams (1g8f46m about f67v; 18k8j2x about f86v, which is locked), cryptophasia (13idzg8), handwriting practice (1bg4s4m), mirror or upside-down reading (123hpg4, ucinry, 1anvmx6), Mongolian, Coptic, Demotic, Glagolitic and Etruscan look-alikes.

---

## 2. Measured or checkable facts

### NEW / worth testing

**2.1 Repeated multi-word sequences are very rare**
- **Post:** w2esca (2022-07-19).
- **Claims:**
  - Marco (Takahashi transcription) found only two repeated 4-word sequences in the whole manuscript. His comparison table is at voynich.ninja thread-2363, post 20335, against KJV Genesis, Dante's Commedia and Pliny of similar word count.
  - The longest repeated chunks (with spelling variation) sit mostly in Q13 and Q20.
  - "No looping" of the kind a mechanical device would produce.
- **Test:** Count repeated 3-, 4- and 5-grams per 10k tokens, exact and within edit distance 1, for:
  - Voynich A and B;
  - 60 languages (equal-size samples);
  - the Timm generator, which copies material and might over-produce repeats;
  - Gaskell–Bowern gibberish.
- **Why it matters:** A symmetric test that either M or L could win.
- **Novelty:** NEW. CLAUDE.md lists word-level repeats (C21, E066) and partners (E069/E070), not repeated phrases.

**2.2 A standalone s occurs much more often just before illustration breaks**
- **Post:** 1574jxc (2023-07-23). Marco reports this from his own study of image breaks; a second user confirms it.
- **Test:** Use the IVTFF interruption markers. Compare the share of one-glyph words immediately before a break with line-internal and line-final positions, and check whether s + next-segment-first-word rejoins into a known type.
- **Novelty:** NEW. It fits with 1.6 above.

**2.3 The star-chart labels are all unique**
- **Posts:** s6ras1 (2022-01-18), about the f68r1 and f68r2 labels; 18cxwp2 (2023-12-07): "remarkably little repetition in star charts".
- **Test:** Compare label repeat rates for star diagrams, zodiac, pharma and herbal labels, against frequency-matched draws.
- **Novelty:** PARTLY TESTED (E056, E059 on label echo; ZODIAC_ONLY_WORDS).

**2.4 Number-like glyph columns beside Arabic numerals 1–5, with a repeating glyph sequence**
- **Posts:** 15axql0 (2023-07-27, said to be "folio 98"); 1f2liob and 1f2lhny (2024-08-27, "page 50, left top corner", probably f49v); 1574jxc.
- **Claim:** The poster matched the shapes to Brahmi-derived numerals, Myanmar closest (4 of 7).
- **Test:** Do these sequences recur elsewhere in ordinal contexts, such as list starts or label sets?
- **Novelty:** PARTLY TESTED (E056 showed zodiac labels are not numbers; this is a different page).

**2.5 Space positions inside long repeated sequences**
- **Post:** 17gmrap (2023-10-26, oshfdk compared spacing and glyph shapes across occurrences of long repeated sequences).
- **Test:** If spaces are mechanical, as E086 found, they should fall in the same places in every repeat.
- **Novelty:** PARTLY TESTED (E086/E092).

**2.6 Counting "one simple edit away" neighbours of each word, Voynich vs Latin**
- **Post:** 17jm7no (2023-10-30, oshfdk, unpublished).
- **Novelty:** PARTLY TESTED (E068's near-copy result NR 1.31; alternations C-facts).

### ALREADY KNOWN / ALREADY TESTED

- **2.7 Exact back-to-back repeats.** About 300 cases, with a longest run of 4 (on locked f75r). Near-repeats differ mostly by q- or by the number of e, rarely by suffix only. Posts: nyzkc9 (2021-06-13), po1xhm (2021-09-14). Already covered by C21, E043, E059 (alternations) and E066. A Pelling post on errors is cited (ciphermysteries 2014-01-15); the error and correction census is still queued in §6 item 6.
- **2.8 ZL word counts.** 36,287 words ignoring uncertain spaces, 39,023 counting them (q54kbp, 2021-10-10). Consistent with E092.
- **2.9 Labels.** Initial q- is rare and o- is frequent (oyeayi comment). Consistent with the label-class facts and E071.
- **2.10 Currier A/B.** A continuum that drifts page by page, including bigram distributions (13mpnt9, 2023-05-20; voynich.nu/extra/curabcd.html). The top-10 words differ by section (1fd6zmc). Consistent with C7/C24 (sheet clustering, E059).
- **2.11 Sukhotin vowel detection is unreliable here** because of the low conditional entropy (umy240, 1574jxc). Bowern & Lindemann find the text unusual at character level but within natural-language range at word and line level (1azdwcn, 1c9... comments). Known.
- **2.12 Codicology.**
  - Drawings came before text (utxvko, 2022-05-20; Zandbergen; D'Imperio 1978).
  - Paint was added after the outlines, possibly by another hand (14ssbk6 comment; 18i30m5).
  - f74 was cut out, with a stub visible, so Aquarius and Capricorn are missing (tjlkub).
  - Quire signatures sit on the last verso of each quire and use Latin abbreviations, with "9" for -us (1b0eh5x, 2024-02-26, about signatures on locked f56v and f8v; Sauvaget's blog, 2012).
  - f1r is a good candidate for the original first page because of its red initials (1ds1hx3).
- **2.13 Materials and dating.**
  - Pigments are cheap and ordinary: azurite blue (McCrone 2009; Zyats et al. 2016 in the Yale facsimile, pp. 33–34; posts 11sws0b, 11tk3hj, 18i30m5).
  - Production cost is about "a couple of months of a skilled artisan's salary" (18i30m5).
  - Costumes date to the 1420s (Gheuens; Roger Wieck; p8myu9, xh3x1e).
  - The crossbow Sagittarius parallels Flemish tapestries of the 1430s (Velinska; 1alcnjs).
  - A German colour note "rot" appears in f4r (nn78me, 1f3oh26).
  - Swallowtail merlons point to Italy or the Alps.
  - Provenance: an earlier owner was a physician living in a botanist's house (15q1gnk; Art Newspaper, 2023-01-13).
  - None of this is testable by us.
- **2.14 Anecdote on mapping tables.** One poster tried 500+ different Voynich-to-Hebrew mapping tables (qes4mc, 2021-10-24). All gave "readable" Google Translate output, and a Hebrew speaker called the output gibberish. This is a live demonstration of the null that E050/E095 guard against. No factor.

---

## 3. Decipherment claims

None of these used a control or null comparison, and none were validated. Rebuttals are summarised.

| Post ids (dates) | Claim | Method | Community rebuttal |
|---|---|---|---|
| mmdf1d, mmtj8s, mn6z8v, moqu0l, mpiyi8, mq1esg, mvtrjs, n14zv2, npbay4, nw8u97, nxgovz, o0fzn6, o58xyd, oaegif, qm3j87, t90sn4, suw4y6 and others (2021–2022, voynichmanuscript.gold, K. M. Tucker; many sock-puppet accounts) | "Galwegian" Middle English / Old Norse merchant argot; nautical maps; Oak Island | Word-by-word etymologies from any language | A posted mapping table turned a herbal line into non-language strings; arbitrary word splitting; no grammar. Users identified sock puppets. |
| mlvzf8, n5sm0e, n9hlxi, nodirw, p81l88, pehqvi, q78l0p, 18cxwp2, 1cy7a7w, 1d0y6pt, 1d33uau, 14max6i (ScienceofGenes / "theoricalist", Persian) | Persian / Farsi | Simple substitution after deleting repetitions (about 30% of characters) | Marco: the qo sequence maps to "KD" in 100% of cases, whereas Persian K is followed by D under 5% of the time. Entropy stays wrong. |
| my148e, nopt5a, peantt, pmkp7a (Domingo Delgado) | Abbreviated Latin | "Permutations" until a Latin word appears | Ungrammatical output. Abbreviation raises entropy (Zandbergen). E053/E071 already exclude this form. |
| po1xhm, 1dqpxay, 1f3oh26, 1f3qr7k (Ardiç family) | Old Turkic | Simple substitution | The EVA -ar ending would be about 7% of words, unlike Turkish. Rejected at peer review (Johns Hopkins, 2016). voynich.ninja thread-2318 was locked. Turkish already tested (E049–E052, E063). |
| t8ta4q, q0mvzo (Gerard Cheshire) | "Proto-Romance" | Ad hoc | Fagin Davis and Ars Technica rebuttals. |
| z7v7on (Rainer Hannig, 2020, in German) | Hebrew | Letter mapping | Not pursued. Covered by the Hebrew campaign (E049, E080–E084, E088–E089). |
| 14elmgh (ResearchGate 368991190, 2023) | Arabic, Bax-style | Labels plus zodiac names | Misreads a Pisces label (two identical glyphs read as different letters). Only 2–3 of 12 zodiac signs "match". Arabic already covered (E063, E088). |
| 1ddis50, 1dl03gm (Eleonora Matarrese, 2024) | Middle High German dialect of Carnia (Timau) | 1:1 substitution; Gart der Gesundheit | A sample from f77r is inconsistent with her own transcription. Sold on Amazon; no peer review. |
| 1d4cp9r (Alisa Gladyseva) | Galician | Unpublished 700 pages | Nothing verifiable. |
| 1e0z0ae, 1e9emij (academia.edu, 2024) | Latin, f1r (locked) | Ignores grammar and spelling | "Ignore spelling, grammar and punctuation" = not a translation. |
| qes4mc, q838wb (2021) | Hebrew via Google Translate | 22-letter table, 500 tables tried | Gibberish according to a Hebrew speaker; see 2.14. |
| 1fksnnp, 1fkzhlj, 1fmd64i (2024) | Basque | Taurus label assumed to be 5 letters; Google Translate | Simple substitution cannot fit Voynich structure (a Gheuens video is cited). |
| 1g30mhk, 1duyzn8, 15axql0, 179uc77, 1fzsbg2, 11lj29p, ubng8f, 17idi7l | Venetic/Faliscan, Coptic, Brahmi numerals, Italian from the f57v wheel, Somali, Latin "qaos" | Shape look-alikes | No method. |
| 16w9yj7, 18n9fir (2023) | "AI" reads "the tagete blooms vigorously" | Unspecified Python model | No method. Tagetes is a New World plant. |
| 126pesq (Bernhart-Königstein, 2023) | Author is Jost of Silenen | A didactic poem | No engagement with the text at all. |
| 1anvmx6 (Kunferman paper; github crknftart) | Mirrored and upside-down text, camera obscura | Stroke-order argument | Google Translate output only. |
| 15gjhdf | "Voynich Cipher Disk" (ResearchGate 360117000) | A wheel per word part; Google Translate | The wheel idea is taken from Zandbergen and uncredited; translations nonsense. The only useful part is idea 1.2. |

---

## 4. Tools, datasets, papers and researchers

### Most useful for the project

- **CEUR-WS Vol-3313**, proceedings of the Malta 2022 conference, free (10aal7y, 2023-01-12). Includes Gaskell & Bowern (paper4) and a Lindemann paper on MATTR. Talk videos: YouTube @VoynichResearchGroup (12adncq).
- **Neural-network transliteration of the Codex Seraphinianus** (Marco Ponzi, Medium "viridisgreen", 162iune, 2023-08-27). The Seraphinianus is a modern asemic text its author says is meaningless, so this is a **known-meaningless control text** for the M-side battery.
- **Zipf comparison of Dee & Kelley's two "angelic" languages** (r/voynich post ephmhy, cited in ucinry). Candidate constructed-language controls, already queued.
- **Zandbergen, "The Cardan grille approach … taken to the next level"**, arXiv 2104.12548, plus Marco's wheel and table (imgur 2r9YOiA). Source for hypothesis 1.2.
- **Hulden (2017), "A phoneme clustering algorithm based on the obligatory contour principle"**, and Marco's Medium post "Bisecting the Voynich manuscript alphabet" (o8bv6q, 2021-06-26). A segmentation / vowel-consonant tool that could be validated on known scripts, then applied to EVA and to glyph-group units (relevant to E092 and the C3 grouping question).
- **Massimiliano Zattera's "slot alphabet"** (1bxvr5t, 1d74ac3); Feaster, Coons and Stolfi on "loops" (Feaster's talk "The Qokeedy and Choldaiin Loops", Voynich Day 2024); Feaster, "Rightward and downward in the Voynich manuscript" (griffonage blog, 2021-08-18), on paragraph and line structure (yl5gni). Relevant to 1.1, E059 and E086.
- **Elmar Vogt, "The Voynich line" (LAAFU)**: voynichthoughts.wordpress.com PDF (1fd6zmc).
- **Bowern & Lindemann 2020**, "The Linguistics of the Voynich Manuscript" (Annual Review of Linguistics; academia.edu 44025265) and arXiv 2010.14697 (character entropy). Their four YouTube lectures (ufh3ri). Reddy & Knight 2011 (ACL W11-1511).
- **Hermann (2017)**, arXiv 1709.01634, on Voynich and the Pahlavi script (1d33uau).
- **Timm & Schinner**, Cryptologia 2023, doi 10.1080/01611194.2023.2225716 (15h6mlz). Generator code: github TorstenTimm/SelfCitationTextgenerator, which the project already has.
- **Fasano**, glossolalia paper (semanticsarchive.net …/The_Voynich_Manuscript_A_Non_Stochastic.pdf), weak.
- **Brewer & Lewis (2024)**, *Social History of Medicine*, "The Voynich Manuscript, Dr Johannes Hartlieb and the Encipherment of Women's Secrets". Lewis also argues for church tapestries as a comparison source (Voynich Day 2024).
- **oshfdk's GitHub "f67r2planets"**: planet and zodiac label matching against the *Opus sphericum* domicile chart, a follow-up on f72r3, a distance-cipher survey (distance.md) and meaning.md (173yz76, 177vowz, 17d4pmw, 17psjqc, 2023).
- **Multispectral imaging of the manuscript, 2024** (Lisa Fagin Davis, manuscriptroadtrip blog, 2024-09-08; posts 1fc8n61, 1fcw2u6).
- **Neural-network handwriting recognition of the Voynich script** (Ponzi, Medium, using Harald Scheidl's software; 10pzzi4, 132tsa3). Suggests an unsupervised alphabet-discovery route.
- **Python package `voynich`** (pip; github jacoblee628/voynich, an IVTFF parser, ru7ke5) and Zandbergen's ivtt tool. The project already has its own parser.
- **Transcriptions:** the Landini–Stolfi interlinear file (voynich.nu/data/beta/LSI_ivtff_0d.txt, with 3–6 transcriptions per line, nw8u97) and Takahashi.
- **Other researchers' material:** Gheuens (SYLORD on glyphhood; the "only 13 letters?" video, 1fydelm; MATTR; costume dating); Cham & Jackson's "curve-line system"; Emma May Smith (agnosticvoynich.wordpress.com; "Feature patterns", Voynich Day 2024); tavie, "Reducing the noise: identifying constraining patterns" (Voynich Day 2024); Stolfi (grammar page; "chinese-redux" word lengths); Bennett 1976 (archive.org); D'Imperio 1978 (NSA PDF; 164g2y6); Pelling (ciphermysteries, on errors); Klaus Schmeh's list of encrypted books (15dll4e).
- **Voynich Day 2024 programme** (1eiayzm): talks by tavie, Gheuens, Zandbergen, Feaster, Brewer, Lewis and Emma May Smith; clips on YouTube.

### Comparison manuscripts (images and layout)

- **Herbals:** the "Alchemical Herbal" (Bodley Canon. Misc. 408, Milan 1378; BNF Lat. 17848; edition by Ragazzini 1983); Trinity O.2.48; the Vermont Herbal; Egerton 747; BSB Cod.Icon.26 and ONB Cod. 5264 (Cadamosto); BNF Lat. 6823 (Manfredus).
- **Other:** Giovanni Fontana's *Secretum de thesauro* (an enciphered machine book c. 1430, decoded by Battisti 1984; npowjd); *Tractatus novus de astronomia* (Library of Congress; slu7jf); Bodley Canon. Misc. 378 (Basel, 1436; wgqzv6); Barb. Lat. 311 (bath scenes; 1c2pnye); Urb. lat. 998 (gallows-like signs; ooc7sq); UPenn LJS 51 (an Arabic cryptography manuscript; 1eznhza); the Llull illustrations (1c2q42c).
- **Possible use:** Fontana and LJS 51 could serve as period cipher-practice references for E098-type classes.

---

## 5. Image identifications supported with evidence

- **f2v: Nymphaea combined with a lily.** Some consensus (Zandbergen's quire page; oc6pxv, 2021-07-02; 1551o48). Evidence: notched leaf and stem; the flower looks like a lily. Not testable by text.
- **f6v: castor bean (Ricinus).** Parallel with Trinity O.2.48 f66v (staj9t, 2022-02-15; sdcrvv). This is the best-supported of the plant identifications here.
- **A locked herbal page (f35v): climbing vine on a support plant.** Parallels BNF Lat. 6823 (Manfredus) f60r (nvbu9t, 2021-06-08; Zandbergen 2016 on stephenbax.net). Vines on another plant are rare in herbals. Locked folio: noted only.
- **f1v: belladonna or nightshade.** Suggested by an anonymous Finnish biologist on stephenbax.net (?p=460; ntjq5a, of0p8e). Animal-root parallels are in the Cadamosto herbal.
- **Viola tricolor** for a locked-folio plant (Sherwood; 1551o48, 16twz66). Locked folio (f9): noted only.
- **Rosettes architecture** matches Bodley Canon. Misc. 378 (Basel, 1436; wgqzv6, 2022-08-05). The Rosettes are on f86, which is locked: noted only. There are also Swiss building comparisons in a 2023 PDF.
- **f67r2 planet and zodiac labels vs the *Opus sphericum* planetary-domicile chart** (oshfdk, 173yz76, 2023-10-09). An overlay gives candidate label-to-planet and label-to-sign matches.
  - **Test:** This could become a planet crib. CLAUDE.md lists no planet-label crib, though E095/E095b/E096 tested the zodiac and degree routes, so this is PARTLY TESTED.
- **Other:** f25v "little dragon" (n1pdod); "human-head roots" occur in other herbals (stephenbax.net ?p=866); f68r3 "Pleiades vs Ursa Minor" (pfx0is, image only). Many other plant identifications in the 2021–2022 series (passion flower, dahlia, cocoa, Kalanchoe) are New World or poorly matched and were challenged in the threads. Not credible.
- **General caution:** Touwaide's view, quoted repeatedly, is that the plants are composites and not identifiable from the drawings alone.

### Notes C

# r/voynich digests 5 and 6: research notes (batch C)

I read both files in full. digest_5.md has 3,717 lines and 216 posts; the first post is 1gba2xp (2024-10-24) and the last is 1py0pi8 (2025-12-28). digest_6.md has 4,120 lines and 213 posts; the first is 1py0qks (2025-12-28) and the last is 1xj2w46 (2026-10-30).

**Rules followed:**
- I copied no EVA text from the locked folios. Where a post concerns f1, f9, f38, f56, f75, f86, f102 or f105, I only name the folio.
- I left out anything about the Indus script.

**Overall:** most posts are AI-generated "translations", image readings or claims of authorship, with no control or null comparison. I list below only the items with real content. Each item is marked:
- **NEW**: not covered by anything in CLAUDE.md;
- **PARTLY**: partly covered by the experiment named;
- **ALREADY**: already tested by the experiment named.

---

## 1. Hypotheses about what the text is (with a mechanism)

### NEW

**H1. Vocabulary "drift": the text changes with position in the book, not with topic** (1v4hiiz, 2026-07-23)
- **Claim:**
  - Word frequencies differ a lot between sections. For example, `ol` occurs 44.4 times per 1,000 tokens in the bathing section but 11.6 in the herbal.
  - The later small-plant pages (f87–f96) do not return to the early herbal vocabulary. Instead they resemble the sections next to them.
  - The words on an identifiable plant page (f2v) are among the most generic in the book.
- **Further claim:** the Naibbe cipher text does not drift at all; its early text looks like its late text. Greshko (the cipher's author) agreed in the comments: his six-table cipher is "flat".
- **Testable:** yes, cheaply. Measure vocabulary similarity between pages as a function of distance in folio order, controlling for Currier language, section, scribe and sheet. Compare Voynich with:
  - Naibbe;
  - the Timm & Schinner generator (self-citation should drift naturally);
  - real books.
- **Why it matters:** this is a feature that could separate copy-type meaningless processes (M) from table ciphers (C). It is a candidate for a test M can win.
- **Status:** PARTLY. E054 (page topics) was VOID; C24/E059 found that pages cluster by sheet; E085 found that same-plant pages share no words. A drift curve with these controls has not been measured.

**H2. Copy-with-mutation ("self-citation") as the generating process, measured with a shuffle control** (1un6p58, 2026-07-04; 1ujflmo, 2026-06-30; 1o25pbj)
- **The metric (1un6p58):** how similar each word is to its recent predecessors, minus the same measure after shuffling the tokens. Shuffling keeps the vocabulary, so word families such as `qokedy`/`qokeedy` add nothing by themselves. The metric also checks for a locality gradient: nearer predecessors should be more similar.
- **Reported numbers:**

  | Text | Copy signal |
  |---|---|
  | Voynich | 0.049 |
  | Every real-text control, including enciphered Latin | ≤ 0.004 |
  | Latin after an "abbreviate + add affixes + re-cut word boundaries" transform | 0.003 |

  That transform does reach Voynich-like h2 and word lengths, but from Latin, English and German alike.
- **1ujflmo:**
  - A plain Markov chain plus a 0.15 chance of copying one of the last 25 words is said to match the text "perfectly". Code: github.com/karolrybak/voynichese.
  - A vision model (qwen3-vl) annotated the images; no word–image correlation survived permutation tests.
- **Testable:** yes. Re-implement the metric and the locality gradient, then run it on Voynich, 60 languages, human gibberish (Gaskell & Bowern), Naibbe and the Timm generator.
- **Status:** PARTLY. It is close to E066 (word individuality), E043/C21 (line recurrence) and the E093 process ladder (no working process found). The specific number, with its locality gradient and the resegmentation control, is new to us. It could also close the "symmetric gap" (a test M can win).

**H3. Other published verbose ciphers that mimic Voynichese (beyond Naibbe)** (1q3n62s, 2026-01-04; 1oii3rm, 2025-10-28; 1szxxtg, 2026-04-30)
- **Greshko lists verbose schemes**, in which one plaintext letter becomes a string of several glyphs:
  - Patrick Feaster's "Griffoynich" (griffonagedotcom.wordpress.com, 2019-04-10);
  - René Zandbergen's "NOT the Solution";
  - Jürgen Hermes's Polygraphia-III-like cipher;
  - the steganographic cipher of Matlach, Janečková & Dostál.
- **1szxxtg ran a 16-property falsification toolkit:**

  | Method | Properties reproduced (of 16) | Notes |
  |---|---|---|
  | Rugg's Cardan grille | 10 | |
  | Naibbe | 8 | |
  | Firth's sorting cipher | 11 | Fails on line-final `m` and on gallows at paragraph start |
  | Timm self-citation | — | "Fails 0/4" |
  | Schinner Markov chain | — | Fails 3 of 4 structural tests |

  The same toolkit measured line self-containment at z = −3.60, which agrees with E086.
- **Testable:** yes. Run Griffoynich, NOT-the-Solution, a Rugg grille and Firth's sorting cipher on E032's 13 features, as E062 and E098 did for other classes.
- **Status:** PARTLY. E062 covered the verbose single-table class (C × 1/3) and E098 covered five period classes. Griffoynich, Rugg's grille and the Firth sorting cipher have not been run on our battery.

**H4. Gallows letters as silent "determinatives" (category markers)** (1sj3vlq, 2026-04-12)
- **Claim:** parsed with the Zattera slot system (prefix + gallows + root + e-chain + suffix), the four gallows letters split by section:
  - t is about 2× enriched on zodiac pages;
  - f is about 3× enriched on herbal pages;
  - p is about 2× enriched in pharma;
  - k is the default.
  
  The gallows × root grid is reported as 68.3% filled, χ² = 879. Repository: github.com/Vineyardcode/voynich_slop. The author admits the work was AI-assisted.
- **Caveat:** p and f sit almost only in the first line of paragraphs (see F3). Herbal pages have many short paragraphs, so the f enrichment may just be a first-line effect.
- **Testable:** yes. Measure gallows × section association controlling for first line, paragraph start, scribe and sheet. Then test the actual determinative prediction: the same root with different gallows should appear in different sections.
- **Status:** NEW as a controlled test. E074/E075 covered slots and piece effects, but not this.

**H5. Paragraph-opening words ("Grove words") are ordinary words with an added gallows** (1qavl2o, 2026-01-12, citing Emma May Smith 2015)
- **Claims:**
  - 58% of pages start with a word that occurs only once in the whole manuscript.
  - The ends of lines also carry recurring one-off words.
- **Testable:**
  1. Remove the first gallows from paragraph-initial words and check whether the remainder is a common word more often than chance, against a generator and against languages with decorated initials. This is the E072 design.
  2. Compare the one-off rate of page-first words with the rate at other line positions and in controls.
- **Status:** PARTLY. LABEL_STEP0 and E075 covered line-start pieces; E072 covered ot/ok detachability. Gallows detachment at paragraph start has not been tested.

**H6. Zodiac label stems sit in fixed ring and clock positions across the wheels** (1pfv59a, 2025-12-06)
- **Claims:**
  - Some stems sit at the same clock-face sector on different wheels; one stem sits at about 5 o'clock on both Taurus wheels.
  - Some stems prefer the inner ring, others the outer.
  - One stem family appears only in Scorpio and Sagittarius.
  - Labels follow a strict root + suffix pattern.
- **Testable:**
  - Ring preference can be tested from the IVTFF locus codes, which give the ring.
  - Clock angle needs coordinates taken from the images. Only DEV zodiac canvases may be used.
- **Status:** PARTLY. CLAUDE.md records that repeated zodiac labels do not sit at the same ring position; E073 and E096 found no link. Stem-level ring preference and sign-specific stem families have not been tested as such.

**H7. "Word reversibility" (Fincher)** (1um5ejs, 2026-07-03)
- **Claim:** a commenter cites Fincher's work on how often word pairs occur in both orders (AB and BA), together with Feaster's `qokeedy` "loop" and autocorrelation. Their conclusion: "either gibberish or heavy nulls/transposition".
- **Testable:** yes. Compute the AB/BA pair-reversal rate for Voynich, the languages, human gibberish and the generator.
- **Status:** NEW. E069/E070 measured how stable word partnerships are across the book, not whether pairs reverse.

**H8. Constructed-language or "compound logograph" reading** (1wsd68q, 2026-09-28; 1wwwxdv)
- **Claim:** glyphs combine into morpheme-like blocks rather than spelling sounds.
- **Measurement idea (1wwwxdv):** compare entropy per pen stroke, or per square centimetre of writing, with contemporary Latin script, rather than entropy per EVA character.
- **Testable:** yes, if each EVA glyph and each Latin letterform is broken into strokes.
- **Status:** NEW as a measurement. The hypothesis itself is untested beyond E065 (the syllable route).

**H9. Two-stage copying: letter-to-glyph mapping, then glyphs sorted inside each word by a "slot alphabet"** (Robert H. Edwards: 1t9wsk9, 1tcr6pt, 1t8xkgq, 2026-05)
- **Objection raised in the comments:**
  - In Italian, letters often repeat within a word.
  - In Voynichese most glyphs occur at most once per word; only minim-like glyphs repeat.
  - A commenter adds that splitting words after minims, plus null sequences, could restore the positional rules.
- **Testable fact:** the rate at which a glyph type repeats within a word, Voynich versus languages and ciphers. This is cheap.
- **Status:** PARTLY. E098 found the in-word sorting class "PARTIAL". The within-word glyph-repetition rate is a clean fact we have not recorded.

**H10. Recipe or formula text: repeated words as dose, time and preparation steps** (1lt4pm6, 2025-07-06)
- **Background:** Trotula-style recipes; the Breviarium Bartholomei (John of Mirfield) put herb names in cipher; Hartlieb called for "secret letters".
- **Testable:** compare Voynich's repetition and partnership statistics with real Latin recipe texts such as Trotula or the Alchemical Herbal (see T5).
- **Status:** PARTLY. E060 (ingredient link) was VOID; E070 lists the catalogue alternative as untested.

### PARTLY or ALREADY tested (brief)

| Item | Posts | Claim | Status |
|---|---|---|---|
| Word ↔ lookup table via 15th-century Italian numerals | 1oyip9h, 1ozhyzi, 2025-11 | Most glyphs match Venetian Arabic-numeral forms (G.F. Hill's 64 tables); a word = table lookup. A commenter notes the first-glyph frequency curve does not break after 10 types, which argues against a 0–9 key. | PARTLY: E056 (not numbers), E098 (nomenclator CLASS FAILS) |
| Alphabetical / partial-order anagram of each word | 1gybt6o, 2024-11-23 | 14 Voynich words are anagrams of the same glyph multiset. A commenter notes alphabetical sorting lowers conditional entropy. Cites Hauer & Kondrak 2016. | ALREADY: E098 (in-word sorting PARTIAL) |
| Anagrammed or "skeletonized" Italian (Sherwood's AVA alphabet) | 1t4frj7, 1taq1fu, 1tbngse | No grammar; unlimited anagram freedom | ALREADY: E098, E049–E052 |
| Hebrew consonant mapping (antenore voynich-toolkit) | 1r8vw3n, 1s2ivxr, 1s4cco3 | Lexicon hits 2–3× a random mapping (z 3.6–4.4), concentrated in Hand 1 and in paragraphs (24.7% vs labels 13.2%), but no readable Hebrew. The author later retracted: the null was a random mapping with no pseudo-Voynich control, and AI-generated "plaintext" fed back through the cipher made false matches. | ALREADY: E049, E050, E080–E084. Their failure confirms that pseudo-Voynich controls are needed. |
| Mirrored / right-to-left Semitic reading | 1qld9jk, 1qvw31t | | ALREADY: E080 (reversed) |
| Abbreviated Latin, Tironian notes, Czech shorthand | 1ndz4t6, 1r3hkk2, 1r5sskh, 1im0d5g | Rebuttal in comments: abbreviation raises character entropy, but Voynich's is low (Lindemann & Bowern 2020). | ALREADY: E053, E071 |
| Simple / frequency-rank substitution (mod-23 decoder; Persian ranking; Slovenian; Irish; Moravian; Hungarian; Turkic) | 1m2hax1, 1vd9102, 1vysrkm, 1w1vga8, 1qgn8ny, 1psy1pf, 1sgnrez | The Irish claimant also "translated" fake Voynichese just as fluently, a self-debunk (1psy1pf). | ALREADY: E047–E052, E063 |
| Musical notation; verse/poetry lowers entropy | 1j6yp98, 1n63nj0 | Iliad character entropy 3.489, so epic verse does not lower it. | PARTLY: E043 genres; hymns are in latin_library_e043 |
| Syllable code / each word a syllable | 1nwo0hb, 1wwwxdv | | ALREADY: E044, E065 |
| Constructed language (Lingua Ignota, Enochian) | 1re2ypo, 1xh4bv3, 1j4zis4 | | NOT DONE: queued as CLAUDE.md §6 item 5 |
| Human glossolalia / spontaneous gibberish | 1o25pbj, 1uf3yw1, 1wqhj82; asemic studies in 1u23ymr | | ALREADY: E045, E067, E068 |
| Pages bound out of order; booklets passed down | see F1 | | PARTLY: C24 |

---

## 2. Measured or checkable facts

### NEW

**F1. Original order of the leaves: Layfield & Fagin Davis** (1oik97p, 2025-10-28; 1pz6yxs, 1pz77va, 2025-12-30; 1x00hs6, 2026-10-07; 1xfluhl, 2026-10-26)
- **Claims:**
  - The manuscript was a set of separate booklets made of single folded sheets ("singulions") before binding.
  - Each folded sheet should be read in full before the next; the current binding nests sheets inside one another.
  - A numerical comparison of text blocks supports this, and plumbing drawn across conjoint leaves is a physical "tell".
  - One comment reports that Layfield's analysis makes f105 the statistical "start" (f105 is locked; I only mention it).
- **Publication:** Digital Medievalist, journals.openedition.org/digitalmedievalist/2331 (the link was given in 1xf64hj). Covered by The Guardian (2026-10-06) and Smithsonian.
- **Checkable:** if the proposed order is published, test whether vocabulary continuity between consecutive pages is higher in that order than in the current order (C24 already says the next page in reading order does not share vocabulary). Also re-check the per-page conditional-entropy "regimes" one comment mentions.
- **Status:** NEW data source; PARTLY consistent with C24/E059.

**F2. Right-margin justification around drawings** (1owa6ag, 2025-11-13)
- **Claim:**
  - On herbal pages the text wraps around the drawings, yet every line ends at the same right margin, with no squeezed glyph spacing and no hyphens.
  - Example given: f36r.
  - The author suggests this means the scribe chose words to fill the space, which points to meaningless text.
- **Counterpoints from commenters:** words are short, so a margin is easy to keep; Italian herbals also break lines mid-word.
- **Testable:**
  - With line widths measured from the images, check whether the length of the last word adapts to the remaining space more than in real herbals.
  - Without images: compare the spread of glyphs per line on wrap-around lines against full-width lines.
- **Status:** NEW. The line-end `-m`/`-y` effects in E075 are related but different.

**F3. EVA p and f almost only in the first line of paragraphs; Grove words** (1kzhkjt, 2025-05-30; 1qavl2o)
- **Status:** ALREADY known on the forum, but it is a needed confound control for H4.

**F4. Missing folios and codicology** (1jsmm5n, 2025-04-06)
- **Facts:**
  - 14 folios are missing by the foliation: 12, 59–64, 74, 91, 92, 97, 98, 109, 110.
  - Missing quires are known from quire numbers.
  - Only f116v has a blank side.
  - f1r is the only page with large painted initials.
- **Status:** facts only; no factor.

**F5. Month names on the zodiac pages were added later** (1i6ctm2; 1tqwwwr, 2026-05-29)
- **Facts:**
  - The month names were probably added around 1500.
  - Their dialect is read as Occitan/Catalan or northern French (Sean B. Palmer's 2004 transcription, inamidst.com/voynich/months).
  - Virgo's month is read as an abbreviated "Septembre".
- **Status:** PARTLY. E094 used the later hand's months.

**F6. A "low-entropy anomaly largely disappears with multigraph signs"** (1uwh5ap, 2026-07-14; AI-assisted)
- **Claims:**
  - Redundancy falls from 0.439 to 0.281 when common EVA sequences count as single signs.
  - Word mutual information persists to about 1,000 words book-wide but fades after 16–64 words within a section.
  - Each zodiac sign has 30 figures (15+15 on Aries/Taurus).
  - The opening words of the 114 herbal pages have "zero overlap" (the post is cut off there).
- **Status:** PARTLY. This matches E092 (space predictability is 0.42 with glyph groups as single signs) and E094 (figures = degrees). The 1,000-word mutual-information claim is unchecked and NEW.

**F7. A "catalogue-style" rewrite of Latin moves character entropy away from Voynich** (1un6p58)
- **Claim:**
  - Rewriting technical or botanical Latin in catalogue style moves its character entropy further from the Voynich value, not closer.
  - Voynich word lengths are unusually uniform.
  - Word-to-word predictability is low.
- **Status:** relevant to E070's untested catalogue alternative; PARTLY.

**F8. Within-word glyph repetition is rare** (1t9wsk9 comment)
- **Status:** see H9; NEW as a recorded fact.

### PARTLY or ALREADY known

| Fact | Posts | Status |
|---|---|---|
| Triple repeats of the same word (an f104v example) and wild `qokeedy`-family runs (f108v) | 1ko8nb6, 1gxl0sw | ALREADY: C21, E043, E066 |
| Line-similarity clustering at threshold 0.6 recovers the section boundaries (bathing ~400 lines; recipes) | 1pq80oi | ALREADY: C7/C24 (sheet and Currier clustering) |
| Character conditional entropy: Irish 3.338 vs Voynich ~2; Latin/Greek 3.5–4+ vs 2.5 (voynich.nu sol_ent) | 1psy1pf, 1tsx6uj | ALREADY: E040, E041 |
| Mean word length too long for an abjad | 1nr8vcp | PARTLY: E088 |
| Benford's law fails (against a ledger reading) | 1wpp231 | ALREADY: E056 |
| Different scribes, shared writing system; Currier A sub-dialects (herbal vs pharma small plants); word shape depends on line and paragraph position | 1k74okz, 1kis75l | ALREADY: E039, E059, E086 |
| Text added after the drawings (it wraps around them) | 1jbwd6p, 1owa6ag | known |
| Zodiac: 30 figures per sign ↔ 360 degrees (Panofsky 1931; Alfonso X manuscripts with 30 radial segments) | 1gfbpqc | ALREADY: E094, E096 |
| Cost: about 2 months of a skilled worker's salary; 1–2 scribe-years | 1osgf5f, 1jbwd6p | not testable |

---

## 3. Decipherment claims (method; controls; rebuttal)

**Pattern:** almost all claims are one-page or few-word "translations" made with an LLM or with free letter-to-sound assignments, and none uses a null or control. Community rebuttals repeat four points:
- there is no grammar or syntax;
- the frequent words are not decoded as function words (the "function-word smoke test", 1s4cco3, 1iqjnht);
- the same Voynich word is translated differently in different places;
- conditional entropy rules out any phonetic mapping.

Only these claims carried any method or control:

| Claim | Posts | Method | Control | Outcome |
|---|---|---|---|---|
| Hebrew consonantal (antenore) | 1r8vw3n, 1s4cco3, 1szxxtg | Mapping optimised against Hebrew lexicons | Random mapping and a synthetic null only | Author retracted ("statistical artifact"). Useful lesson for our controls; ALREADY E049/E080. |
| mod-23 inverse decoder | 1m2hax1 | Shuffled-alphabet Monte Carlo (10,000 runs); out-of-sample bigram prediction | Shuffled alphabets | It is a simple substitution; the author conceded entropy cannot change. ALREADY E047. |
| Naibbe cipher (Greshko, *Cryptologia* 2025, open access; GitHub repo) | 1n080et, 1p9f8cr, 1q3n62s, 1v4hiiz | Proof of concept, scored on Gaskell & Bowern 2022 measures | — | Not a solution; lacks long-range correlations and line-position effects (author agrees). ALREADY: E086 (spaces 0.67), E062. |
| Jessica Scott (Dunn) "Compendium" (Latin + German, Clemens Specker as author, healing oils) | 1gq59dl, 1gm29xh, 1r3hkk2, 1r5sskh, 1ra4mhh | Letters changed freely | None | Moderators flagged it as spam; ALREADY E053 |
| Irish / Christine de Pisan (TikTok) | 1j57tli, 1o1u3c5, 1psy1pf | Phonetic mapping | None; she "decoded" fake Voynichese equally well | Rebutted |
| Italian anagram / "skeletonized Italian" (f99r, f2r) | 1t4frj7, 1taq1fu, 1tbngse | | None | Rebutted |
| Persian letter-frequency ranking (Robert H. Edwards, "Voynich Reconsidered", Medium/Substack) | 1vd9102, 1viunq7, 1vysrkm, 1w1vga8, 1w9mg17 | Rank matching; "permutations" of transliterations × languages, scored by number of real words | No null for how many real words chance gives | ALREADY: E047 class |
| Zuger Functional Decipherment (github.com/denoflore/ZFD); "Generative instruction set" (Zenodo 16981869); Voynich Engine (Zenodo 20185824) and others | 1wiinv6, 1phfm72, 1td5rp4 | | None | Low value |
| Others with no method: Kitano (Japan), Fletcher Crowe (Cathars), Bruno Borges, Moravian, Slovenian, Yiddish, "VX-2025 key", and many AI posts | various | | | Low value |

---

## 4. Tools, datasets, papers and researchers we may lack

### NEW or useful

**Comparison texts and manuscripts**

| Item | Posts | Use |
|---|---|---|
| LJS 51 (Penn), *Collection of Alphabets and Encoded Correspondence* (Syria, 15th c.), archive.org/details/ljs51 | 1ljxq2f | Period cipher alphabets with Voynich-like signs |
| LJS 419 / Alchemical Herbal ("Erbario"), archive.org/details/ljs419; plain-text transcription and translation by a commenter on Medium (medium.com/viridisgreen) | 1wrk860, 1tx4dd8, 1ndz4t6 | Candidate period herbal/catalogue control text for E070 |
| *Shénnóng běncǎo jīng*, Classical Chinese herbal on ctext.org | 1ry1za1 | Isolating-language herbal catalogue control (Stolfi's Chinese idea) |
| Trotula (Liber Trotula viewer B_OB_MS593); Breviarium Bartholomei (John of Mirfield, some herb names in cipher); John de Foxton, *Liber Cosmographiae* (partly ciphered medical words) | 1lt4pm6, 1vn8x90 | Recipe-genre and partial-cipher medical controls |
| Cgm 384 (BSB, 15th-c. Alemannic miscellany of recipes and charms); parallel to f116v marginalia | 1wsc456 | Context for the f116v charm |
| Cod. Sang. 754 (St Gallen, 1466); plant drawing in Voynich-like style; "leber" handwriting like f116v; Brian Cham 2014 | 1qcqaq3 | Image and handwriting comparison |
| Morgan M.384, *Von dem Gang des Himels und Sternen*; Diebold Lauber workshop | 1ibou7l | Zodiac image sources |
| Heidelberg Cod. Pal. germ. 330 | 1gftf2a | Nymph proportions |
| Basel UB A XI 61 | 1gypvwy | Unpunctuated 15th-c. German text |
| Giovanni Fontana's cipher manuscripts | 1utf6xa, 1gypvwy | Plain red initials and pilcrows |
| G.F. Hill, *The development of Arabic numerals in Europe* (64 tables; HathiTrust) | 1ozhyzi | Numeral glyph forms |
| Cappelli abbreviations online (centerfordigitalhumanities.github.io/cappelli) | 1r5sskh | Abbreviation reference |

**Papers**
- Lindemann & Bowern 2020, "Character Entropy in Modern and Historical Texts" (arXiv 2010.14697). It covers EVA and a minimal transcription, and finds that abbreviation *raises* entropy.
- Bowern & Lindemann 2021, *Annual Review of Linguistics*.
- Voynich 2022 conference proceedings (CEUR Vol-3313):
  - paper4: Gaskell & Bowern, gibberish;
  - paper9: Lindemann;
  - paper12: Feaster, line effects;
  - keynote2: Fagin Davis, scribes.
- Feaster's blog: "Rightward and downward" (2021, line-level structure) and "Griffoynich" (2019).
- Timm, arXiv 1407.6639.
- Hauer & Kondrak 2016, TACL Q16-1006 (decoding anagrammed texts).
- PMC8794160: gallows as ligatures.
- PMC6424067: asemic text.
- Huh et al. 2024 (the "platonic representation" of language models).
- Digital Medievalist 2331 (Layfield & Davis; see F1).

**Researchers and talks**
- Tavi Stafford (line effects, Voynich Day 2024).
- Emma May Smith (Grove words).
- J.K. Petersen, voynichportal (gallows, pilcrows, garbled plant labels).
- Brian Cham's "curve-line system" (1pxjuwd): many glyphs differ only by a curved versus a straight base stroke. This could be tested as a hidden feature.
- Koen Gheuens (VoynichTalk).
- Nick Pelling (proposed DNA tests of the vellum, 1wr99zz).
- Edith Sherwood (plant IDs; AVA alphabet).
- Lisa Fagin Davis's talks (YouTube nH28ltqYIyo; Getty talk).

**Software tools**
- Zandbergen's STA (Super Transliteration Alphabet) and CUVA (1gyb5yb). STA encodes the shape variants of the `sh` plume. An idea from the comments: do the variants behave differently, e.g. does a word ending pair with one plume shape but not another?
- extended EVA reference (voynich.nu/hist/gabriel/eva2_reference.pdf).
- QuireLab (quirelab.vercel.app; entropy, Zipf, sections).
- xkortex infographics: glyph position within words, and a reader (xkortex.github.io/voynich_infographics).
- voynichese.com (XML EVA under the Apache licence).
- bi3mw.lima-city.ch (syllable heat map).
- James Tauber's byte-pair encoding as a structural probe (voynich.jtauber.com).
- VoynichFramework.com (generator-class tests).
- github.com/antenore/voynich-toolkit (16 falsification phases).
- github.com/karolrybak/voynichese (Markov + self-citation).
- jasondavies.com/voynich (zoom viewer).
- A depainting model (oshfdkbw.pages.dev).
- A commenter training an OCR model on the Yale scans (1x8qmv1). It is reported to find letters not in ZL, and to split some "unique" glyphs into two ordinary ones. This is relevant to E092 and a planned correction census.

**Forum threads**
- voynich.ninja plant polls: threads 4630 and 4637.
- Naibbe discussion: thread 5081.
- Debunk of the Slovenian theory: thread 4758.
- 2026 conference call: thread 5274.
- f116v charm: thread 5162.

---

## 5. Image identifications supported with evidence

| Identification | Posts | Evidence | Status |
|---|---|---|---|
| Sagittarius with crossbow = 15th-c. German motif (voynich.nu illustr.html#zodi2); clothing styles of the early 1400s; ghibelline swallowtail merlons point to northern Italy or the Alpine area | 1s4d8lt, 1ov84ea, 1r32l3t | Comparison with dated motifs | Known; supports dating |
| Zodiac images copied from a German tradition: Morgan M.384 (Aries/Leo poses, ground and trees) and the Diebold Lauber workshop (Gemini) | 1ibou7l | Side-by-side comparison | Plausible; image-only |
| f9v = *Viola tricolor* | 1ra4mhh | Named as the most solid ID; f9 is LOCKED, so I only mention it | — |
| Maidenhair fern | 1ra4mhh | Mentioned as "quite positively identified", without evidence | — |
| f6v castor bean (*Ricinus*), via Trinity College MS O.2.48 | 1hgrs0c | Comparison with that manuscript | — |
| Rosette foldout outer ring = four elements (Sacrobosco 1490 diagram) | 1w2hqfa | Shape match for two of four markings | Weak |
| T-O map on the cosmological page | 1nf0qy5, 1qqx2gd | Glyphs placed as Asia/Africa; substituting them gives no useful result | Known |
| Faces in plant roots, as in Alchemical Herbal copies (Florence BBU 106 f17v) | 1mxb5su | Precedent shows such drawings are not unusual | Context only |
| Others (Socotra plants, sunflower, cloudberry, mushrooms, organs, neurons, uterus, beekeeping on a locked folio) | various | No evidence | Not useful |

Not testable but noted: 1rimh1q; 1o0u28k (green stars on f68, crossbowman's chaperon hat); 1ridqva (f67 day/night clock giving a latitude).
