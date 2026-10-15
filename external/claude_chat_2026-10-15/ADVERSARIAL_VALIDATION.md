# ADVERSARIAL_VALIDATION — Agent F (independent adversarial reviewer), OPERATION EXEMPLAR
Date 2026-10-15. Scope: claims (1)–(5) as stated by the PI. All work is in `workstreams/agent_f_adversarial/`. I wrote no files outside this directory.

## Bottom line
| # | Claim | Verdict |
|---|---|---|
| 1 | Positive control: re-coded plants are retrieved at median rank 1–2 | **CERTIFY** (it is a test-retest reliability result only) |
| 2 | f35v↔Lat.6823 Edera is mutual-asymmetric; 61–68% of Voynich plants have a best match at least this good | **CERTIFY** (numbers reproduce exactly; they make the link look weak) |
| 3a | P-fam PASS | **CERTIFY** (robust in 8/8 scorer variants) |
| 3b | P-voy FAIL; Voynich matches Ashmole "as well as or better" | **DOWNGRADE**: FAIL is robust (7/8). "Better than the Tractatus pool" is not robust: it depends on the colour fields and reverses without them |
| 3c | P-ivy: mutual #1 with Sloane; Lat ranks f35v #1; Ashmole ranks f35v #2 | **DOWNGRADE**: the Chigi entry is a code bug, and the result is not specific to the family. Details below |
| 4 | The composite "berry-bearing climber wound round a separate host trunk with an oak-like crown" occurs only in the Tractatus ivies and in f35v | **REJECT** for f35v. The source side holds: in the sources I checked, this composite is Tractatus-specific |
| 5 | S1–S4 frozen predictions (1 pass, contaminated) | **REJECT as evidence**. The freeze cannot be verified, and one pass in four is what chance gives |

**Sign-off for the f35v ↔ Tractatus-ivy correspondence: L0, and a weak one.** I do not sign the PI's "L0+ (shared rare composite)". The rare composite is not present in f35v when the image is read strictly (§4). After correction for multiple comparisons the correspondence is not significant (§d). Nothing here reaches L1 or L2.

---
## (a) Coder independence and the scratchpad collision
**Facts:**
- The Egerton log (`code_egerton747/logs/view_log.csv`, last line) says a shared `scratchpad/dl.py` was overwritten "by another workstream", and that two Egerton runs executed that foreign script.
- The surviving `scratchpad/dl.py` (mtime 09:52:50 IST) is the **Ashmole 1431** downloader. It writes only to `code_ashmole1431/raw/`, takes URLs only from `raw/ashmole1431_sample.csv`, and skips any existing file larger than 10 kB.
- Sloane also ran a `scratchpad/dl.py` earlier (its stdout shows a different version).

**Was Ashmole data affected? No.**
- `code_ashmole1431/logs/downloads.log` has exactly 37 lines, one per canvas, all between 04:22:52 and 04:26:02 UTC, with no duplicate folios.
- The file mtimes match those timestamps one-to-one. All 37 images have the expected IIIF sizes (1200 px singles, 2400 px openings).
- Any later run of the script by Egerton would have skipped every file and written nothing. This matches Egerton's own note: "no output observed".
- The script cannot write Egerton or Sloane images into the Ashmole folder, or the reverse.
- The Egerton download log contains only Egerton URLs, the Sloane log only Sloane URLs, and the Ashmole log only Bodleian URLs.

**Verdict:** the collision is a hygiene failure with no data effect.

**Other independence issues I found:**
1. **The ivy entries were targeted, not sampled.**
   - Sloane 038v lies outside the random sample. It was fetched specifically to find the E-section ivy (RESULTS.md says so).
   - Chigi 35r and 36r were opened while searching for the ivy.
   - Every control coder's RESULTS.md has an "Ivy" section, so the coders knew ivy was of interest.
   - The coders did not see Voynich images (the logs agree, and the coders say so). Even so, the two rows that drive P-ivy were coded by people looking for ivy.
2. **One model codes everything.** All coders are instances of the same model. Their independence is procedural, not cognitive, so shared lexical habits ("oak-like", "host") can create cross-corpus matches in the free-text fields.
3. **No Egerton ivy is coded.** Egerton 037r is not in the sample; the coder notes the ivy text on 037v. P-ivy's "every family ivy" therefore covers only 3 of the 4 Tractatus witnesses.

## (b) How sensitive are P-voy and P-ivy to the scorer?
Script: `sensitivity.py`, which re-implements `fastscore.py` with configurable fields and weights. Output is in `sensitivity_results.json` and `logs/sensitivity_stdout.txt`. The "PI primary" variant reproduces the PI's figures: P-fam margin 2.359; P-voy margin −0.52 against the PI's −0.545, a difference due only to the random seed.

**Code bug in `tradition_test.py` P-ivy.**
- The ivy selector matches the strings `'edera'` and `'hedera'`. The Chigi ivy row is labelled `Eder[a] nigra`, so the bracket defeats the match.
- The selector therefore picked row 35v,3, labelled "? (host tree of Edera)". That is the oak host tree, not the ivy.
- The PI's Chigi P-ivy entry (f35v rank 2, ivy rank 6) is the host tree's result.
- On the correct row, Chigi ivy and f35v are **mutual #1, with a score of 21.17**. That is identical to Sloane, because the two coders gave the same categorical codes apart from the berry count.

| Variant | P-fam | P-voy margin (threshold) | LAT ivy: f35v rank / ivy rank for f35v | SL ivy | CH ivy (corrected) | ASH ivy (control) |
|---|---|---|---|---|---|---|
| PI primary (rarity) | PASS | −0.52 (1.18) FAIL | 1 / 12 | 1 / 1 | 1 / 1 | **2** / 4 |
| uniform weights | PASS | +0.29 (0.64) FAIL | 2 / 3 | 1 / 1 | 1 / 1 | 19 / 4 |
| free-text secondary | PASS | −0.61 (1.23) FAIL | 1 / 12 | 1 / 1 | 1 / 1 | 2 / 5 |
| drop colour fields | PASS | +0.45 (0.47) FAIL (marginal) | 2 / 11 | 1 / 1 | 1 / 1 | **1** / 3 |
| drop twining | PASS | −0.53 (1.22) FAIL | 1 / 6 | 1 / 2 | 1 / 2 | 8 / 8 |
| drop twining + stem_type | PASS | −0.48 (1.24) FAIL | 1 / 2 | **2** (f17v #1) / 3 | **2** (f17v #1) / 6 | 66 / 70 |
| uniform + drop colour | PASS (margin 0.19, 2sd 0.16) | +0.11 (0.09) **PASS** | **7** / 3 | 1 / 1 | 1 / 1 | 12 / 4 |
| drop colour + twining + stem_type | PASS | +0.41 (0.55) FAIL | 1 / 1 | 2 / 3 | 2 / 6 | 52 / 53 |

**What can be read off the table:**
- **P-fam is robust.** The method detects the Egerton→Lat.6823 family signal under every scorer.
- **The P-voy FAIL is mostly robust.** It flips only in one variant, where P-fam itself barely passes.
- **The P-voy direction is not robust.** VOY→ASH > VOY→TRAC holds only when colour is weighted. Without colour, or with uniform weights, the margin is positive: Voynich is nearer the Tractatus pool, but below the pre-registered threshold. The PI's phrase "Voynich matches Pseudo-Apuleius as well as or better than the Tractatus pool" should become: "no Tractatus-specific signal above the pre-registered threshold; the sign of the small difference depends on the scorer."
- **P-ivy ranks mostly survive.** The pre-registered criterion (f35v ranks ≤3 for every coded family ivy) holds in 7 of 8 variants. It fails under uniform + drop colour, where the Lat ivy ranks f35v 7th.
- **P-ivy is not specific to the family.**
  - Under the PI's own scorer, the non-Tractatus control ivy (Ashmole, Pseudo-Apuleius, no host tree) ranks f35v **#2**. With colour dropped it ranks f35v **#1**.
  - The high Sloane and Chigi scores (21.17) depend on the twining and stem_type fields. Drop both and f17v overtakes f35v, and f35v ranks those ivies only 3rd and 6th.
  - In most variants the runner-up behind f35v for the Sloane and Chigi ivies is **f49r**, which matters for §c.
  - The Lat.6823 link does not depend on twining, because the Lat ivy is coded twining=no. But from f35v's side it is weak: under the PI scorer Edera is only #12 for f35v. f35v's best Lat match is Cucumeres (21.8 and 23.3 across the PI and pooled runs).

## (c) Is f35v unique, and is there a host trunk? (images viewed with the Read tool)
**Images viewed:**
- f35v at 2400 px, with crops of the base and upper part (`view/f35v_base.jpg`, `view/f35v_upper.jpg`).
- f49r at 2000 px.
- A contact sheet of f17v, f41v, f49r, f51v, f96v and f3v.
- Lat.6823 060r, full page and ivy crop.
- Sloane 4016 f38v and Chigi F.VII.158 f35v.
- Egerton 747 f103v.
- The PI's panel.

**The Tractatus ivies:** in all three, the host is a different plant.
- **Sloane 038v:** a thin brown ivy stem spirals tightly up a thick speckled trunk. The trunk carries a crown of oak leaves and ends at the lower margin with no root. The ivy has star-shaped leaves and black berry umbels.
- **Chigi 35v:** the ivy spirals up a pale, rootless pole with an oak crown, in barber-pole style.
- **Lat.6823 060r:** nature-printed ivy leaves are fixed directly to a straight, pale, rootless trunk, with an oak branch at the top.
  - I see **no winding**. The coder's twining=no is correct.
  - So in the PI's anchor witness the climber is not "wound round" anything. "Wound round a host" fits Sloane and Chigi only.
  - The PI's panel crops Lat 060r below the oak crown. I recommend recropping so the crown is visible.

**f35v:** the "host trunk" reading does **not** hold up.
1. The central trunk and both lateral stems rise from **one and the same root crown**. They share one green wash and one pen outline, and they join at the same point on the large brown spreading root (`view/f35v_base.jpg`). Nothing marks the trunk as a second plant: there is no separate base, no different colour or bark, and no cut end.
2. The lateral stems cross the trunk twice, loosely, like a braid. That is not the tight helix of Sloane and Chigi.
3. The **oak-like lobed leaves are borne on the lateral (climbing) stems**, not on the trunk's crown. The crown is a dense mass of sinuous foliage that rises from a fan of fine lines at the top of the trunk. The Tractatus layout puts oak leaves on the host and ivy leaves on the climber; f35v reverses this.
4. The diagnostic ivy features are absent:
   - There are no star-shaped 3–5-pointed leaves.
   - The berries are blue-green (2 clusters are red-brown), not black.

**Is f35v unique within the Voynich?**
- **f49r has the same architecture:** a straight central stem, wavy lateral stems crossing back and forth over it, about 20 small red bud or berry clusters on those lateral stems, and two big crown-like leaf masses at the top, all from a single root. Its coding (twining=yes, stem_type=twining, berry_cluster, lobed_rounded) almost duplicates f35v's.
- **f51v** has strap leaves wound around a central stem and berries.
- **f17v** has berry clusters and a tendril coiling on itself, but no trunk.
- **f41v** has two stems twisting over each other, but no berries.
- **f96v** has hanging berry clusters, but no twining or trunk.

What is unique to f35v is only the pair of oak-like leaves combined with the braided stems. And "oak-like" is a coder word: the Voynich coder uses it again at f44v, for a bare trunk with an oak-like crown.

**Corpus search** (fields + `distinctive_features`, pooled over 1,059 rows, file `all_corpora_pooled.csv`):
- **A climber on a separate host also occurs outside the ivy entries:**
  - Egerton 103v *Viticella*: berry-bearing climbing stems winding through a neighbouring plant. I checked the image. This row is also the **mutual-best partner of f49r (score 23.34)**, a stronger pair than f35v–ivy.
  - Lat 060v *Epithymum*: dodder wound over a host bush.
  - Lat 063v *Ebulus*: a snake coils up the stem (not a plant).
- "Host" and "support" appear only at the Sloane and Chigi ivy and host rows, at Lat 060r and Lat 060v, and at Sloane 031v (a building supporting Cimbalaria).
- **Oak-like crowns** also appear at Egerton 032v (Dragagantus) and Voynich f44v.
- **Conclusion:** the full source-side composite (berried ivy wound round a separate oak-crowned trunk) is confirmed only at the Tractatus ivies. In the Voynich, the "climber + trunk + clusters + crown" schema is a recurring Voynich architecture (f35v, f49r), and in f35v the "host" is the plant's own stem.

## (d) Correction for multiple comparisons
Script: `look_elsewhere.py`, with output in `look_elsewhere.json`. It uses the PI primary scorer with rarity weights computed on the full pool. The search covers Voynich (124 plants) × Tractatus witnesses (LAT, SL+SLx, CH+CHx, EG), which is 84,072 pairs.
- **Pairs as good as the ivy:** 7 pairs (8.3e-5 of all pairs) reach at least the f35v–Sloane/Chigi ivy score of 21.17, spread over 4 Voynich plants.
- **Mutual-best pairs scoring ≥21.17** within a single witness pool, 6 in all:
  - f35v–Cucumeres (LAT, 23.32)
  - f49r–Viticella (EG, 23.34)
  - f18v–"Bebun" (CH, 21.5)
  - f19r–Galitricum (SL, 21.34)
  - f35v–Edera (SL, 21.17)
  - f35v–Edera (CH, 21.17)
- **Null model:** Voynich codes shuffled column-wise, 300 replicates. P(at least one such mutual-best pair) = **0.71**, with a mean of 1.23 pairs per replicate.
- **Same-species mutual-best matches in two witnesses also occur for other plants:** f56v↔Agrimonia (LAT and CH) and f20r↔Ysopus (SL and CH). Finding agreement across witnesses is therefore not rare either. It is also not independent evidence, because the witnesses copy one another, so their codes are correlated by construction.
- **Answer to (d):**
  - Within this coded sample, the probability that some Voynich plant shows a match to some Tractatus plant as specific as f35v–ivy is about **0.7 under the shuffled null**. The observed value is 1: it happened at least 4 times.
  - The original lead came from a public search over roughly 120 Voynich plants and hundreds of herbal images, with many proposed identifications collected by Zandbergen. That search space is larger still, so the corrected p is about 1.
  - **The f35v–ivy correspondence carries no significance after correction.**

## (e) Is the composite a generic medieval ivy convention?
**Sources reached:**
1. **Bodl. Ashmole 1431 fol. 25v** (Pseudo-Apuleius, already coded): *hedera nigra* is a free looping red stem with a root knob and no host or tree.
2. **Gart der Gesundheit, Augsburg 1487** (reprint of Mainz 1485), archive.org `mobot31753000814712`, pages n202–n203, chapter clxiii "Edera arborea / yſen oder ebich".
   - I located the chapter through the OCR and the printed heading. Assigning the woodcut to the chapter by the book's layout convention is medium-confidence.
   - The woodcut is a free-standing branched sprig with small umbels of round fruits or buds, and no host or twining.
   - The text says "edera schlinget sich auf ein andern baum" (ivy winds itself onto another tree), yet the picture shows no tree.
   - View: `view/gart1487_ivy.jpg`.

**Not reached:** Commons searches for Tacuinum sanitatis and the Carrara Herbal (Egerton 2020) were blocked by HTTP 429 even after back-off (`logs/commons_search.log`). Carrara derives from Lat.6823 in any case and would not be an independent test.

**Result:** in two non-Tractatus traditions, ivy is drawn **without** a host tree. Drawing a host appears to be a **Tractatus-family convention, not a generic one**. This strengthens the source-side claim 4. It does not rescue the Voynich side, because the host element is not present in f35v (§c).

## Claim-by-claim

### (1) Positive control — CERTIFY (scope-limited)
- **Attack:** I re-ran `positive_control.py` and it reproduces exactly (primary median 2, top-1 0.475; secondary median 1).
- **Scope:** this is a retest of the same image, retrieved within its own corpus. It measures how reliable a coder is, not whether the method transfers across manuscripts. Transfer across manuscripts is what P-fam tests.
- **Field agreement between the two codings:** twining 0.92, leaf_color 0.90, leaf_margin 0.88, fruit_color 0.85, flower_or_fruit_type 0.70, root_type 0.65, leaf_shape 0.62, stem_type 0.57, leaf_arrangement 0.57, symmetry 0.57, height_width_ratio 0.55.
- Two items fail outright, at ranks 263.5 and 264.5 (Lat 171r:2 and 066v:1).
- The stem_type agreement of 0.57 matters: the strongest ivy link (Sloane/Chigi at 21.17) depends on stem_type=twining.

### (2) match_tests — CERTIFY (numbers)
- `match_tests.py` reproduces exactly: score 12.98; Edera ranks 12 of 269 for f35v; f35v ranks 1 of 124 for Edera; 67.7% (primary) and 61.3% (secondary) of Voynich plants have a best match at least this good.
- The real-versus-shuffle z of 5.6–7.4 is a generic effect of within-plant correlation between fields. It is not evidence of a source relationship.
- Read correctly, the result says f35v–Edera is an unremarkable pair.

### (3) Tradition test — P-fam CERTIFY; P-voy DOWNGRADE (wording); P-ivy DOWNGRADE
- P-ivy has the Chigi row bug. Correcting it makes the PI's number *stronger*, so the bug ran against the PI.
- P-ivy cannot tell the family from the control: the Ashmole ivy ranks f35v #2, or #1 with colour dropped.
- It depends on the twining and stem_type fields.
- Egerton's ivy is untested.
- P-ivy should be reported as "f35v is the Voynich plant nearest to any berried twining climber in this scorer", not as a family-specific hit.

### (4) Iconographic composite — REJECT (Voynich side); CERTIFY (source side, Tractatus-specific)
See §c and §e. In f35v the "host" is the plant's own central stem, rooted in the same root. The oak-like leaves sit on the climbers, the ivy diagnostics are absent, and f49r repeats the architecture.

**A residual hypothesis remains.** A Voynich artist might have conflated host and ivy into one rooted plant. That would explain the shared root and the swapped leaves. But it is post hoc and cannot be tested with the present data.

### (5) S1–S4 — REJECT as evidence
- **The freeze cannot be verified:**
  - The predictions say "freeze time recorded by git commit", but `/home/claude/exemplar` is **not a git repository** (`git status`: "not a git repository").
  - `FROZEN_PREDICTIONS_f35v.md` (10:11:30.68) and `f35v_structural_results.json` (10:11:31.54) were written **0.86 s apart**.
  - No scoring script is preserved anywhere I could find, so the results cannot be reproduced.
- **The PI had already seen the f35v page,** as the predictions themselves disclose.
- **One pass in four is what chance gives:**
  - S4 is uninformative by its own rule, because 94.5% of first tokens are unique.
  - With 3 informative tests at α=0.10, P(at least one pass by chance) ≈ 0.27.
  - S1 sits at the 98.8th percentile, nominal p ≈ 0.012, or ≈ 0.04 after Bonferroni correction over 3 tests. That is at most suggestive, and with the contamination it cannot be assessed at all.
- **S3 fails:** f35v has a single paragraph, which goes against the recipe-block expectation.

## Requests to the PI before any write-up
1. Fix the P-ivy row selector (match `eder` or use explicit row IDs) and re-issue `tradition_test.json`.
2. Re-word P-voy as in §b.
3. Drop "separate host trunk" from the f35v description. Describe f35v as "lateral berry-bearing stems braided round the plant's own central stem".
4. Recrop the Lat 060r panel so the oak crown shows.
5. Code the Egerton 747 ivy on 037r.
6. Put the project under real version control before calling any further prediction "frozen". Save the S1–S4 scoring script.

## Files (this directory)
| File | Contents |
|---|---|
| `sensitivity.py`, `sensitivity_results.json`, `logs/sensitivity_stdout.txt` | Analysis (b) |
| `look_elsewhere.py`, `look_elsewhere.json`, `logs/look_elsewhere_stdout.txt` | Analysis (d) |
| `all_corpora_pooled.csv` | Pooled coded rows used for the §c corpus search |
| `rerun/` | Exact re-runs of the PI's `positive_control.py` and `match_tests.py` |
| `raw/f35v_2400.jpg`, `raw/f49r_2000.jpg`, `raw/gart1487_n202.jpg`, `raw/gart1487_n203.jpg` | Images retrieved; listed in `sources.csv` and `logs/downloads.log` |
| `view/` | Downscaled crops actually viewed |
| `logs/commons_search.log`, `logs/archive_search.log` | Access attempts for (e) |