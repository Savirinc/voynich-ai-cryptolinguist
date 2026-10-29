"""Parse the Skyscript degree table (Lilly, Christian Astrology 1647 pp. 116-118, with Al-Biruni variants marked *)
into reports/data/degree_tables.json: sign -> 30 rows {deg, term, face, gender, light, others}."""
import html, json, re, sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="latin-1").read()
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
rows = re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S)
T, cur = {}, []
for r in rows:
    tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
    if len(tds) < 7:
        continue
    tds = tds[-7:]
    deg = re.sub(r"<[^>]+>|&nbsp;|\s", "", tds[0])
    if not deg.isdigit():
        continue
    alt = lambda c: (re.findall(r'alt="([^"]+)"', c) or [""])[0]
    txt = lambda c: html.unescape(re.sub(r"<[^>]+>", " ", c)).replace("\xa0", " ").strip()
    row = {"deg": int(deg), "term": alt(tds[1]), "face": alt(tds[2]), "gender": txt(tds[3]), "light": txt(tds[4]), "others": " ".join(txt(tds[5]).split())}
    if row["deg"] == 1 and cur:
        T[SIGNS[len(T)]] = cur; cur = []
    cur.append(row)
T[SIGNS[len(T)]] = cur
assert len(T) == 12 and all(len(v) == 30 for v in T.values()), {k: len(v) for k, v in T.items()}
json.dump({"source": "skyscript.co.uk/deginf.html (Lilly CA pp.116-118; * = Al-Biruni Elements 457-458 variant)", "tables": T}, open(out, "w"), indent=1)
for k, v in T.items():
    print(f"{k:12s} G " + "".join(r["gender"][0] for r in v) + "  L " + "".join(r["light"][:1] or "?" for r in v))
