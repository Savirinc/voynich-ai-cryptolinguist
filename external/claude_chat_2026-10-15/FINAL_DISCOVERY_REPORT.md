# OPERATION EXEMPLAR — Final discovery report
**Date:** 15 October 2026 · **Repository:** `/home/claude/exemplar` (git) · **Outcome: no source relationship established. Highest evidence level reached: L0 (weak visual resemblance), certified by the adversarial reviewer.** No semantic anchor was found; nothing was predicted about the meaning of any Voynich text.

## 1. Bottom line
1. **The f35v ↔ BnF Lat. 6823 f60r (Edera nigra) lead is traceable but not a source relationship.** It originates with René Zandbergen (Villa Mondragone slides, 11 May 2012). Both folios were retrieved and verified from primary scans (Yale IIIF; BnF scans via Wikimedia Commons, since gallica.bnf.fr is Cloudflare-blocked from here). f35v does resemble the Tractatus-family ivy more than most plants do, but the resemblance is (a) shared by an unrelated-tradition ivy, (b) matched or exceeded by other Voynich↔source pairs, and (c) not significant after correcting for the search that found it (look-elsewhere p ≈ 1).
2. **The Voynich herbal shows no tradition-level relationship to the Tractatus de herbis family.** The pre-registered test passed its positive control: the method detects the known Egerton 747 → Lat. 6823 kinship, and recovers Sloane 4016 as Lat. 6823's closest relative, consistent with the published stemma. It then found that Voynich drawings match the unrelated Pseudo-Apuleius herbal (Ashmole 1431) as well as or better than the Tractatus witnesses (VOY→TRAC − VOY→ASH = −0.55; threshold for a family signal +1.18). The FAIL holds in 7 of 8 scorer variants.
3. **No textual correspondence (L2) was possible.** The Latin ivy entry was fully transcribed and source-traced. But with no independently established folio pair, there was nothing to fit a mapping on and nothing to predict. Structural predictions for f35v passed 1 of 4 (chance ≈ 0.27), and the passing one was contaminated by prior viewing of the page.

## 2. What was done (all reproducible; see EXPERIMENT trail below)
| Step | Result |
|---|---|
| Primary images | Voynich f35v (Yale IIIF canvas 1006143); Lat. 6823 ff. 59v–60v (Commons, 1280–1920 px) |
| Diplomatic transcription + translation | Lat. 6823 *Edera nigra*: 74 lines, ≈97% of lines high-confidence; *Enula campana* ≈70%; `LATIN_SOURCE_TRANSCRIPTIONS/` |
| Source tracing of the Latin | Three blocks: Latin Dioscorides II "de cissos" (alphabetical recension, = 1478 Colle edition), Latin Dioscorides I (cistus/hypocistis/ladanum confused with ivy), and 7 "Ad …" recipes from Pseudo-Apuleius c.100 labelled "Plinius". Circa instans has no ivy chapter. |
| Genealogy | 18-witness Tractatus stemma; Lat. 6823 dated c.1330–40, place disputed (Milan / Campania / Padua / Siena); Manfredus herbals in the Pavia Visconti library inventory of 1426 (identification of no. 923 with Lat. 6823 contested); `MANUSCRIPT_GENEALOGY.md` |
| Blind iconographic coding (fixed 22-field schema, coders never saw the other corpus) | Lat. 6823 269 plants · Egerton 747 102 · Sloane 4016 116 · Chigi F.VII.158 181 · Ashmole 1431 148 · Voynich 124 = **940 coded drawings, 6 manuscripts** |
| Retrieval positive control | 40 random plants independently re-coded: true item retrieved at median rank 1–2 (top-10 85–88%) vs chance ~62–135. Certified as coder reliability, not cross-manuscript transfer. |
| Pre-registered tradition test | P-fam PASS (Egerton→Lat 16.12 vs Ashmole→Lat 13.76, ≈21 sd) · **P-voy FAIL** |
| Ivy-specific test (4 ivies) | f35v ranks #1 for the Lat. 6823, Sloane (f38v) and Chigi (f35v) ivies, and #2 for the unrelated Ashmole ivy (f25v). Driven by twining + stem_type: drop those two fields and f17v overtakes f35v. |
| Look-elsewhere | 6 Voynich↔Tractatus mutual-best pairs score ≥ the ivy pair (3 belong to f35v itself, incl. *Cucumeres*); shuffled data produce ≥1 such pair 71% of the time |
| Adversarial review | `ADVERSARIAL_VALIDATION.md`; sign-off **L0 (weak)** |

## 3. The ivy convention, examined directly (IMAGE_PANELS/ivy_comparison.jpg)
- **Egerton 747 f37r (archetype, c.1280–1310):** ivy alone, star-shaped leaves, thin stem twisting round itself, small berry clusters; **no host tree.** Rubric: *"Edera nigra arbor est quam greci vocant cisso melle, galli vocant…"*
- **Lat. 6823 f60r (c.1330–40):** nature-printed ivy on a straight stem with oak-like lobed leaves at the top; not wound round anything.
- **Chigi F.VII.158 f35v (c.1400) and Sloane 4016 f38v (Lombardy c.1440):** ivy explicitly spiralling up a *separate* host trunk crowned with oak-like leaves; black berry umbels.
- **Ashmole 1431 f25v (Pseudo-Apuleius) and Gart der Gesundheit 1487:** no host tree.
- **Voynich f35v:** a central stem plus two stems winding round it, all rising from one root crown; oak-like lobed leaves; berry clusters on short stalks, blue-green (two brownish); no star-shaped ivy leaves; large spreading root.

**Reading:** the oak-host composite is a development *within the Lat. 6823 branch*, not a family-wide or generic convention. f35v lacks its defining element (a separate host plant) and the ivy's diagnostic leaves. The shared elements — twining stems, berry clusters, lobed leaves — are common enough that f49r has the same architecture, and Egerton's *Viticella* matches f49r more strongly than any ivy matches f35v.

## 4. Falsified / downgraded / surviving
**Falsified:** a Tractatus-family source for the Voynich herbal as a whole (at the sensitivity of this method, which detects Egerton↔Lat. 6823 kinship at ≈21 sd). That f35v copies the Lat. 6823-branch "ivy on oak" composite (no separate host). That f35v's text has an Edera-entry structure (1/4 predictions, contaminated).
**Downgraded:** "f35v ↔ Lat. 6823 f60r" from published lead to L0, look-elsewhere-corrected p ≈ 1.
**Surviving, weakly:** f35v may depict a climber of ivy type. That is a plant identification at L0, not a source link, and it cannot anchor meaning.
**Not tested (inaccessible or out of budget):** Morgan M.873, Modena (Estense), Casanatense 459, Masson 116, the French *Livre des simples* branch, the Veneto "alchemical herbals" (stylistically the closest analogues to Voynich in the literature), Carrara Herbal, Tacuinum sanitatis, Arabic/Byzantine materia medica; the zodiac, balneological and pharmaceutical sections; gallica (blocked); Wikimedia began rejecting requests as robot traffic late in the run.

## 5. Why external evidence did not break the underdetermination
A source relationship needs a *distinctive* shared feature whose co-occurrence is improbable under independent drawing. The Voynich herbal drawings sit, statistically, as close to an 11th-century English Pseudo-Apuleius as to the Italian Tractatus family. The one family-specific ivy convention found is absent from f35v, and the best single-pair matches arise as often from shuffled codings. Without a folio pair whose link is established independently of the Voynich text, the decisive experiment (Stage 4–5: fit a mapping on one pair, predict another) cannot start.

## 6. What would change this
1. **The highest-value next step:** code the Veneto/Lombard "alchemical herbals" (e.g. Florence, Vicenza, Trento copies cited by Segre Rutz and Touwaide) with the same schema. These are the manuscripts most often called stylistically closest to the Voynich, and none was reachable here.
2. Code every Tractatus witness reachable by IIIF (Morgan M.873, Casanatense 459, Modena) to test the Lat. 6823 branch specifically against Voynich, with Pseudo-Apuleius as the null.
3. Any candidate pair must clear a look-elsewhere-corrected threshold before text work begins; then two or more independent pairs are needed for a fit-one/predict-one test.

## 7. Process corrections recorded
- The PI's initial description of the f35v "host trunk" and of Lat. 6823's ivy as "wound round" its host were wrong; both were corrected by Agent F and by direct inspection of Egerton 747 f37r.
- P-ivy originally scored Chigi's host tree instead of the ivy (string-match bug); fixed in `tradition_test_v2.*`. The fix strengthened, not weakened, the ivy score, and changes no conclusion.
- The f35v structural predictions were written 0.86 s before scoring, in an unversioned directory; they are reported as exploratory only. The project is now under git.
- The census agent (A) was terminated by a usage-limit error before writing output; the census was rebuilt from the genealogy agent's stemma and the coding workstreams.
- All coders were the same model family: independence was procedural (separate contexts, no shared files), not methodological.

Sources: [Yale Beinecke MS 408](https://collections.library.yale.edu/catalog/2002046) · [BnF Latin 6823 notice](https://archivesetmanuscrits.bnf.fr/ark:/12148/cc13456t) · [Wikimedia Commons BnF Latin 6823 scans](https://commons.wikimedia.org/wiki/Category:BnF_Latin_6823) · [Zandbergen 2012 slides](https://www.voynich.nu/papers/Voynich100_RZ_2012.pdf) · [Bodleian MS. Ashmole 1431](https://medieval.bodleian.ox.ac.uk/catalog/manuscript_253) · [Ashmole 1431 IIIF via Biblissima](https://iiif.biblissima.fr/collections/manifest/e89c8e5ce2c3acf37e65544ef2f12bb7c2e0879b) · [BAV Chig. F.VII.158](https://digi.vatlib.it/view/MSS_Chig.F.VII.158) · [Latin Dioscorides ed. Hofmann–Auracher/Stadler](https://archive.org/details/b24880796) · [Pseudo-Apuleius edition](https://archive.org/details/BIUSante_41488x01) · [Circa instans, Lyon 1582](https://archive.org/details/BIUSante_pharma_res012103)