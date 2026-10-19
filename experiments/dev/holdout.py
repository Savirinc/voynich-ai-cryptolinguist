"""Hold out whole Latin Library files as plaintext: CALIB (dev calibration) and TEST (reserved for the locked E027
known-answer test). Files are picked by a seeded shuffle among files with >= 30k clean words; removed from the LM."""
import json, random, pickle
from latseg import X, NX
keep = json.load(open(X + "latlib_keep.json"))
words = {}
for f in keep:
    w = [w for w in (NX.clean(x) for x in open(X + "lat_text_latin_library/" + f, errors="ignore").read().split()) if w]
    words[f] = w
big = sorted(f for f in keep if len(words[f]) >= 30000)
rng = random.Random(27027); rng.shuffle(big)
calib, test = big[:6], big[6:16]
print(len(big), "files >= 30k words"); print("CALIB", calib); print("TEST", test)
pickle.dump({"calib": {f: words[f] for f in calib}, "test": {f: words[f] for f in test}}, open(X + "latlib_hold.pkl", "wb"))
lm = [w for f in keep if f not in calib + test for w in words[f]]
pickle.dump(lm, open(X + "latlib_words_lm.pkl", "wb")); print("LM words", len(lm))
json.dump({"calib": calib, "test": test}, open("holdout_files.json", "w"), indent=1)
