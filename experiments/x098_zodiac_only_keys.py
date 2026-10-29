"""X098 (exploratory, Arham 2026-10-29): keys under which zodiac-only Voynich words read EXACTLY as zodiac material of
their own page's sign. Words: reports/data/zodiac_only_words.csv (345). Units: E024 S3 glyph units. Material per sign:
E095 meaning lists in 8 languages (two months, sign, animal, planet, element, season) and the fixed-star names of that
sign in the period degree table (reports/data/degree_tables.json). A key maps each unit to one letter (several units may
share a letter). Exact whole-word match, read forwards. For each source, randomised greedy search for keys matching as
many different words as possible; the best distinct keys are listed.
Run: .venv/bin/python experiments/x098_zodiac_only_keys.py
"""
import csv, json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments"))
import e024_atoms as A24  # noqa: E402
from e040_clean_profile import n1  # noqa: E402

SEED, RESTARTS, TOP = 98098, 3000, 3
CON = json.loads((ROOT / "reports/data/e095_concepts.json").read_text())
TAB = json.loads((ROOT / "reports/data/degree_tables.json").read_text())["tables"]
HEB = dict(zip("AbgdhwzHTyklmnsEpcqrSt", "אבגדהוזחטיכלמנסעפצקרשת"))
ARA = dict(zip("AbtVjHxdDrzsSCQTZEGfqklmnhwy", "ابتثجحخدذرזسشصضطظعغفقكلمنهوي".replace("ז", "ز")))
MONTH = {"feb": "February", "mar": "March", "apr": "April", "may": "May", "jun": "June", "jul": "July", "aug": "August",
         "sep": "September", "oct": "October", "nov": "November", "dec": "December"}


def material(lang, sign):
    if lang == "star names":
        return STARS[sign]
    a = CON["attributes"][sign]; L = CON["languages"][lang]; out = []
    for m in a["months"]:
        out += [(w, f"month: {MONTH[m]}") for w in L["months"][m]]
    out += [(w, f"sign name: {sign}") for w in L["sign"][sign]] + [(w, f"animal/figure of {sign}") for w in L["animal"][sign]]
    out += [(w, f"planet: {a['planet']}") for w in L["planet"][a["planet"]]]
    out += [(w, f"element: {a['element']}") for w in L["element"][a["element"]]]
    out += [(w, f"season: {a['season']}") for w in L["season"][a["season"]]]
    return out


def load_stars():
    """fixed-star names per sign and degree: last column of the Skyscript (Lilly) degree table"""
    import html, re
    raw = (ROOT / "data/external/degree_tables_x097/deginf.html").read_text(encoding="latin-1")
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    out, cur, k = {}, [], -1
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)[-7:]
        if len(tds) < 7:
            continue
        deg = re.sub(r"<[^>]+>|&nbsp;|\s", "", tds[0])
        if not deg.isdigit():
            continue
        if deg == "1":
            k += 1; out[signs[k]] = []
        txt = html.unescape(re.sub(r"<[^>]+>", " ", tds[6])).replace("\xa0", " ")
        for nm in re.split(r"[,()]", txt):
            nm = " ".join(nm.split())
            if nm:
                out[signs[k]].append((nm, f"fixed star at {signs[k]} {deg} deg"))
    return out


def script(lang, w):
    if lang == "hebrew":
        return "".join(HEB.get(c, c) for c in w)
    if lang == "arabic":
        return "".join(ARA.get(c, c) for c in w)
    return w


def main():
    rng = random.Random(SEED)
    words = []
    for r in csv.DictReader(open(ROOT / "reports/data/zodiac_only_words.csv")):
        us = tuple(A24.segment(n1(r["word"]), A24.SEGS["S3"]))
        for p in r["pages"].split(";") if ";" in r["pages"] else r["pages"].split(","):
            p = p.strip()
            if p in CON["pages"]:
                words.append((r["word"], us, p, CON["pages"][p]))
    sources = list(CON["languages"]) + ["star names"]
    report = {}
    for src in sources:
        cand = []
        for w, us, p, s in words:
            mats = material(src, s)
            for t, gloss in mats:
                t2 = t if src in ("hebrew", "arabic") else "".join(c for c in t.lower() if c.isalpha())
                if len(t2) != len(us):
                    continue
                m, ok = {}, True
                for u, c in zip(us, t2):
                    if m.setdefault(u, c) != c:
                        ok = False; break
                if ok:
                    cand.append((w, p, s, t, t2, gloss, tuple(sorted(m.items()))))
        found = {}
        for _ in range(RESTARTS):
            order = cand[:]; rng.shuffle(order); key, got = {}, []
            for c in order:
                if all(key.get(u, l) == l for u, l in c[6]):
                    for u, l in c[6]:
                        key[u] = l
                    got.append(c)
            ws = frozenset((c[0], c[1]) for c in got)
            if ws not in found:
                found[ws] = (dict(key), got)
        best = sorted(found.values(), key=lambda kg: -len({c[0] for c in kg[1]}))
        out, seen = [], []
        for key, got in best:
            wset = {c[0] for c in got}
            if any(wset <= s for s in seen):
                continue
            seen.append(wset); out.append({"key": key, "matches": [c[:6] for c in got]})
            if len(out) == TOP:
                break
        report[src] = {"candidates": len(cand), "words_with_any_fit": len({c[0] for c in cand}), "keys": out}
        print(src, "words with any single fit:", len({c[0] for c in cand}), "| best key words:", [len({m[0] for m in k["matches"]}) for k in out], flush=True)
    (ROOT / "experiments/results/x098.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))


STARS = {}
if __name__ == "__main__":
    STARS.update(load_stars())
    main()
