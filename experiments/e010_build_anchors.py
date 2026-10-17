"""E010 part 1: build data/derived/anchors_v1/anchors.jsonl (candidate semantic anchors, confidence-graded).

Voynich side: label / first-word text from the local ZL3b IVTFF (vcl.corpus.ivtff via vcl.anchors).
Meaning side: short factual items (folio, proposed meaning, proposer, citation) from published listings; no prose
is copied. Every row records whether its leaf is LOCKED_TEST (eval/PROTOCOL_v1.md section 1); locked rows are
stored but flagged `usable=False` and are excluded from every analysis.

Tiers:  A = meaning written in a known script on the page (month names)   B = published identification with
>=2 proposers from independent lineages agreeing (genus level)   C = single proposer/lineage or contested
D = visual resemblance only (L0).  Lineages: Th. Petersen's list, Ethel Voynich's notebooks (which drew on Petersen)
and the ZL3b 'Plant ID' comments (which reproduce Petersen's notes) count as ONE lineage; O'Neill, Holm, Sherwood,
Velinska, Bax, Tucker & Talbert are separate proposers (they are not necessarily independent: most had seen
earlier lists).

Run: .venv/bin/python experiments/e010_build_anchors.py
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.anchors import ZODIAC, _lines, _parsed, first_word, locked_leaves, page_labels, zodiac_pages  # noqa: E402
from vcl.corpus.ivtff import DOCX_SHA256  # noqa: E402

OUT = ROOT / "data/derived/anchors_v1/anchors.jsonl"
ACC = "2026-10-17"
SRC = {
    "vnu_writing": {"source": "R. Zandbergen, voynich.nu 'Extraneous writing' (writing.html)",
                    "url": "https://www.voynich.nu/writing.html", "accessed": ACC},
    "vnu_q10": {"source": "R. Zandbergen, voynich.nu quire 10 page descriptions",
                "url": "https://www.voynich.nu/q10/index.html", "accessed": ACC},
    "vnu_q11": {"source": "R. Zandbergen, voynich.nu quire 11 page descriptions",
                "url": "https://www.voynich.nu/q11/index.html", "accessed": ACC},
    "vnu_oldid": {"source": "R. Zandbergen, voynich.nu 'Old plant identifications' (Petersen; E. Voynich notebooks "
                            "at Grolier Club and Beinecke; inline O'Neill and Holm attributions), updated 2016-12-03",
                  "url": "https://www.voynich.nu/extra/herb_oldid.html", "accessed": ACC},
    "vnu_illustr": {"source": "R. Zandbergen, voynich.nu 'Illustrations' (herbal, astronomical, pharma notes)",
                    "url": "https://www.voynich.nu/illustr.html", "accessed": ACC},
    "zl3b": {"source": "ZL3b IVTFF transcription (Zandbergen-Landini) v3b 13/05/2025, page comments",
             "url": "local:data/raw/handoff/source_dump/IVTFF Eva.txt.docx", "sha256": DOCX_SHA256},
    "bax2014": {"source": "S. Bax (2014) 'A proposed partial decoding of the Voynich script', v1, January 2014 "
                          "(read via Wayback Machine copy)",
                "url": "https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf",
                "accessed": ACC},
    "sherwood2013_via_bax": {"source": "E. Sherwood (2013), as quoted/cited in Bax 2014 (primary not consulted)",
                             "url": "https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf",
                             "accessed": ACC},
    "velinska2013_via_bax": {"source": "E. Velinska (2013), as cited in Bax 2014 (primary not consulted)",
                             "url": "https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf",
                             "accessed": ACC},
    "tucker_talbert2013": {"source": "A.O. Tucker & R.H. Talbert (2013) HerbalGram 100:70-85, as summarised by "
                                     "N. Pelling, Cipher Mysteries 2014-01-21 (primary not consulted)",
                           "url": "https://ciphermysteries.com/2014/01/21/brand-new-new-world-nahuatl-voynich-manuscript-theory",
                           "accessed": ACC},
    "exemplar": {"source": "Operation Exemplar final report (this repo), 2026-10-15",
                 "url": "local:external/claude_chat_2026-10-15/FINAL_DISCOVERY_REPORT.md"},
    "vnu_labels": {"source": "R. Zandbergen, voynich.nu label analysis (299 zodiac labels, 80% hapax)",
                   "url": "https://voynich.nu/extra/labels.html", "accessed": ACC},
}

# --------------------------------------------------------------------------- curated plant / star / pharma rows
# (folio, meaning, proposers[list], sources[list], tier, contested, alternatives, voynich_side, note, verified)
# voynich_side: ('first_word',) | ('label', locus) | ('word', locus, eva)
CURATED = [
    ("f2r", "Centaurea (cornflower/knapweed genus)",
     ["O'Neill (Cyanus silvestris)", "Holm (Centauria)", "Sherwood 2013 (Centaurea diffusa)", "Velinska 2013",
      "Bax 2014"], ["vnu_oldid", "zl3b", "sherwood2013_via_bax", "velinska2013_via_bax", "bax2014"], "B", False,
     ["E. Voynich: Cyanus?"], ("first_word",),
     "Bax reads the first word as a Centaurea name; genus-level agreement across lineages", True),
    ("f9v", "Viola tricolor (pansy, herba trinitatis)",
     ["O'Neill (herba trinitatis)", "Petersen", "E. Voynich (Viola; Beinecke notebook 'Pansy ++')"],
     ["vnu_oldid", "zl3b"], "B", False, [], ("first_word",), "leaf 9 is LOCKED_TEST", True),
    ("f18r", "Calendula (marigold)",
     ["O'Neill (Ringelblume)", "Petersen (Calendula officinalis)", "E. Voynich (Aster? Calendula)"],
     ["vnu_oldid"], "B", False, ["Aster"], ("first_word",), "", True),
    ("f32r", "Mentha (mint)",
     ["O'Neill (Mentastrum)", "E. Voynich (Mentha; Beinecke 'some kind of mint')"], ["vnu_oldid", "zl3b"], "B",
     False, ["Prunella vulgaris (Petersen)"], ("first_word",), "", True),
    ("f90r1", "Papaver (poppy)", ["Holm (Papaver somniferum)", "E. Voynich (Papaver)"], ["vnu_oldid"], "B", False,
     [], ("first_word",), "", True),
    ("f29v", "Nigella sativa (black cumin)", ["Sherwood 2013", "Velinska 2013", "Bax 2014"],
     ["sherwood2013_via_bax", "velinska2013_via_bax", "bax2014"], "B", False, [], ("first_word",),
     "identification reported via Bax 2014; Sherwood/Velinska primaries not consulted", True),
    ("f3v", "Helleborus (hellebore)", ["Sherwood 2013 (H. foetidus)", "Bax 2014"],
     ["sherwood2013_via_bax", "bax2014"], "C", False, [], ("first_word",),
     "Bax's reading builds on Sherwood's ID (one lineage)", True),
    ("f16r", "Juniperus oxycedrus (juniper)", ["Bax 2014 (with S. Peterson: 'could be possible')"], ["bax2014"],
     "C", True, ["Cannabis (Petersen)", "Aconitum? (E. Voynich)"], ("word", "f16r.10", "toror"),
     "Bax: 'oror' pattern in first word of last paragraph; also 'orom' at end of f16r.1", True),
    ("f41v", "Coriandrum sativum (coriander)", ["Sherwood 2013", "Bax 2014"],
     ["sherwood2013_via_bax", "bax2014"], "C", True, ["Daucus (E. Voynich)", "fern/tansy (Petersen)",
                                                      "plain carrot (RZ, ZL comment)"], ("label", "f41v.1"),
     "Bax's 'marginal word' above the first line; ZL records it as plant label f41v.1", True),
    ("f31r", "Gossypium (cotton)", ["Bax 2014"], ["bax2014"], "C", True,
     ["Hyoscyamus/henbane (Petersen; E. Voynich; Beinecke)"], ("first_word",), "Bax: ID 'requires verification'",
     True),
    ("f27r", "Crocus / Colchicum ('kesar')", ["Bax 2014"], ["bax2014"], "C", True,
     ["Asarum (Petersen)", "Datura? (E. Voynich)"], ("first_word",), "Bax: ID 'difficult ... with any certainty'",
     True),
    ("f1v", "xiuhamolli (soap plant, New World)", ["Tucker & Talbert 2013"], ["tucker_talbert2013"], "C", True,
     ["Atropa belladonna / Solanum (Petersen; E. Voynich)"], ("first_word",),
     "leaf 1 is LOCKED_TEST; T&T species-level name not verified from primary", False),
    ("f35v", "ivy-type climber (Hedera; cf. BnF Lat. 6823 f60r 'Edera nigra')",
     ["Zandbergen 2012 (lead)", "Operation Exemplar 2026 (certified L0)"], ["exemplar", "vnu_illustr"], "D", True,
     ["uva quercina / grapevine (Petersen; E. Voynich)"], ("first_word",),
     "Operation Exemplar: highest level reached L0 'weak visual resemblance'; look-elsewhere p~1; leaf 35 LOCKED_TEST",
     True),
    # star / astronomical
    ("f68r3", "Taurus / Pleiades (label next to a 7-star cluster)", ["Zandbergen 2004-2013 (as cited by Bax)",
                                                                    "Bax 2014"],
     ["bax2014", "vnu_illustr"], "C", True, [], ("word", "f68r3.11", "doaro"),
     "Pleiades identification of the star cluster is iconographic; which ZL locus Bax's word is was inferred by us "
     "from his description ('to the right of the seven stars'), not checked against the image", False),
    # pharma
    ("f100r", "pepper (Piper)", ["O'Neill 1944"], ["vnu_illustr"], "C", True, [], ("page",),
     "voynich.nu: 'no longer generally accepted'; exact drawing/label not resolved here", True),
    ("f93r", "sunflower (Helianthus)", ["O'Neill 1944"], ["vnu_oldid", "vnu_illustr"], "C", True, [],
     ("first_word",), "voynich.nu: 'no longer generally accepted'; New-World plant, contradicts radiocarbon date", True),
]

MARGINALIA = [
    ("f116v", "Latin-script text mixing pseudo-Latin and German; ZL comment gives fragments incl. "
              "'valsch vbren so nim gaf mich o' and 'michiton oladab...'; two Voynich words 'oror sheey' on the "
              "same line", ["vnu_writing", "zl3b", "bax2014"],
     "no Voynich word is glossed; Bax notes 'oror' also occurs here"),
    ("f66r", "German words near a reclining figure, read 'der Mussdel' (R. Salomon) or 'Musmel' (Zandbergen); "
             "neither accepted", ["vnu_writing"], "Voynich labels nearby; no gloss relation established"),
    ("f17r", "largely unreadable top-margin comment; Voynich-script words visible under UV (Pelling)",
     ["vnu_writing"], ""),
    ("f1r", "ex libris of Jacobus de Tepenec; letter tables in right margin (later decryption attempt?)",
     ["vnu_writing"], "leaf 1 LOCKED_TEST"),
]


def plant_id_comments() -> dict[str, str]:
    """ZL3b '# Plant ID:' comments per folio (Petersen-lineage notes), joined with continuation lines."""
    lines, out, cur = _lines(), {}, None
    for i, l in enumerate(lines):
        s = l.strip()
        m = re.match(r"^<(f\w+?)>", s)
        if m:
            cur = m.group(1)
        if s.startswith("# Plant ID:"):
            txt = s[len("# Plant ID:"):].strip()
            if txt.endswith(","):
                txt += " " + lines[i + 1].strip().lstrip("# ").strip()
            out[cur] = txt[:120]
    return out


def main():
    pages = _parsed()[0]
    locked = locked_leaves()
    rows = []

    def base(folio):
        leaf = pages[folio].leaf
        return {"folio": folio, "leaf": leaf, "section": pages[folio].illustration, "locked": leaf in locked}

    # (a) zodiac: tier A, page-level (the Voynich word that would carry the month, if any, is unknown)
    for zp in zodiac_pages():
        r = base(zp["folio"])
        labels = [l["eva"] for g in zp["label_groups"] for l in g["labels"]]
        r |= {"id": f"zod_{zp['folio']}", "anchor_type": "zodiac_month", "tier": "A",
              "proposed_meaning": f"{zp['month_modern']} (sign: {zp['sign']})",
              "meaning_text_on_page": zp["month_latin_script"], "meaning_text_zl_comment": zp["month_zl_comment"],
              "meaning_script": "Latin script, later hand (15th c. per forum/paleographer reports; unverified)",
              "meaning_language": "a form of French per Zandbergen (disputed: Occitan / Alemannic proposals)",
              "voynich_side": "page-level: one of the page's labels or circular-text words (unknown which, if any)",
              "voynich_locus": None, "voynich_eva": None, "candidate_labels": labels,
              "n_candidate_loci": len(labels), "proposers": ["later owner/reader (annotation on the page)"],
              "sources": [SRC["vnu_writing"], SRC["vnu_q10" if zp["folio"].startswith("f70") else "vnu_q11"],
                          SRC["zl3b"], SRC["vnu_labels"]],
              "contested": False, "alternatives": [],
              "note": "month name was added by a later hand: it records a later reader's reading of the sign, "
                      "not necessarily the author's text; f73r/f73v descriptions on voynich.nu q12 not fetched",
              "verified": True}
        if zp["folio"] == "f70v1":
            r["note"] += "; spelling conflict: ZL comment 'Abril' vs voynich.nu 'aberil'"
        if zp["folio"] == "f72r2":
            r["note"] += "; reading 'jong' vs 'yony' disputed (forum discussion)"
        rows.append(r)

    # (b)-(c) curated plant / star / pharma
    curated_folios = set()
    for folio, meaning, props, srcs, tier, contested, alts, vside, note, verified in CURATED:
        curated_folios.add(folio)
        r = base(folio)
        if vside[0] == "first_word":
            loc, eva, basis = f"{folio}:first_word", first_word(folio), "first word of page (Stolfi/Zandbergen hypothesis that it names the plant)"
        elif vside[0] == "label":
            lab = [x for x in page_labels(folio) if x["locus"] == vside[1]][0]
            loc, eva, basis = vside[1], lab["eva"], "plant label"
        elif vside[0] == "word":
            loc, eva, basis = vside[1], vside[2], "word singled out by proposer"
        else:
            loc, eva, basis = None, None, "page-level only"
        kind = {"f68r3": "star_label", "f100r": "pharma_label"}.get(folio, "plant_id")
        r |= {"id": f"{kind}_{folio}", "anchor_type": kind, "tier": tier, "proposed_meaning": meaning,
              "voynich_side": basis, "voynich_locus": loc, "voynich_eva": eva, "n_candidate_loci": 1 if eva else None,
              "proposers": props, "sources": [SRC[s] for s in srcs], "contested": contested,
              "alternatives": alts, "note": note, "verified": verified}
        rows.append(r)

    # (b) remaining Petersen-lineage IDs recorded in the ZL transcription itself: tier C (single lineage)
    for folio, txt in sorted(plant_id_comments().items(), key=lambda kv: (int(re.match(r"f(\d+)", kv[0]).group(1)), kv[0])):
        if folio in curated_folios or not re.search(r"[A-Za-z]{3}", txt) or "unreadable" in txt.lower()[:15] \
                or "hard to read" in txt.lower() or "too many" in txt.lower():
            continue
        r = base(folio)
        tags = re.findall(r"\((O'Neill|O'N|Holm|RZ|R\. Zandbergen|Mrs Voynich|Voynich|Manley)\)", txt)
        r |= {"id": f"plant_id_{folio}", "anchor_type": "plant_id", "tier": "C", "proposed_meaning": txt,
              "voynich_side": "first word of page (Stolfi/Zandbergen hypothesis that it names the plant)",
              "voynich_locus": f"{folio}:first_word", "voynich_eva": first_word(folio), "n_candidate_loci": 1,
              "proposers": ["Petersen lineage (ZL3b 'Plant ID' comment)"] + sorted(set(tags)),
              "sources": [SRC["zl3b"], SRC["vnu_oldid"]], "contested": "?" in txt or "," in txt,
              "alternatives": [], "note": "multiple candidate names in one list entry count as contested",
              "verified": True}
        rows.append(r)

    # (d) marginalia: text only, not usable as word anchors
    for folio, desc, srcs, note in MARGINALIA:
        r = base(folio)
        lab = page_labels(folio)
        r |= {"id": f"marg_{folio}", "anchor_type": "marginalia", "tier": "A",
              "proposed_meaning": None, "meaning_text_on_page": desc, "voynich_side": "none (no gloss relation)",
              "voynich_locus": None, "voynich_eva": None, "candidate_labels": [x["eva"] for x in lab][:10],
              "n_candidate_loci": None, "proposers": [], "sources": [SRC[s] for s in srcs], "contested": True,
              "alternatives": [], "note": note, "verified": True}
        rows.append(r)

    for r in rows:
        r["usable"] = (not r["locked"]) and r["anchor_type"] != "marginalia"
        r["word_level"] = r["usable"] and r.get("voynich_eva") is not None
        if r["locked"]:
            r["note"] = (r.get("note", "") + "; LOCKED_TEST leaf: stored only, excluded from all analyses").lstrip("; ")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    print(len(rows), "rows ->", OUT.relative_to(ROOT), hashlib.sha256(OUT.read_bytes()).hexdigest()[:12])
    print("by tier (all):", dict(Counter(r["tier"] for r in rows)))
    print("by tier (usable word-level):", dict(Counter(r["tier"] for r in rows if r["word_level"])))
    print("locked:", [r["id"] for r in rows if r["locked"]])


if __name__ == "__main__":
    main()
