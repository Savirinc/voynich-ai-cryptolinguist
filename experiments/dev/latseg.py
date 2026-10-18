"""Stage B dev, compound (stem + ending) probes: shared Latin segmentation and data.
seg(w): longest matching inflectional ending from a fixed list, stem >= 3 letters; words < 4 letters unsplit
(ending '')."""
import sys, json, pickle, os
sys.path.insert(0, "/Users/arhampartapjain/voynich-ai-cryptolinguist/src")
sys.path.insert(0, "/private/tmp/claude-501/-Users-arhampartapjain/88643098-eceb-4bf4-97b5-9edd541be4ec/scratchpad")
from wordsub_proto import words_of, NX
X = "/private/tmp/claude-501/-Users-arhampartapjain/88643098-eceb-4bf4-97b5-9edd541be4ec/scratchpad/ext/"
END = """a ae am arum as is os us i o um orum e em es ibus ium u ui uum ei erum er
o as at amus atis ant eo et emus etis ent it imus itis unt abat abant ebat ebant abam
avit averunt avi isse it ere are ire ari eri iri atur antur etur entur itur untur tur ntur
ndum ndi ndo nda ndae ns ntis nte nti ntem ntes ntium ntur tus ta tum ti tae tos tas tis to
erat erant esse issent isset asset aret eret iret aret arent erent irent"""
END = sorted(set(END.split()), key=len, reverse=True)
def seg(w):
    if len(w) < 4: return w, ""
    for e in END:
        if w.endswith(e) and len(w) - len(e) >= 3: return w[:-len(e)], e
    return w, ""
def latlib():
    p = X + "latlib_words.pkl"
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    ref = []
    for f in json.load(open(X + "latlib_keep.json")):
        ref += [w for w in (NX.clean(x) for x in open(X + "lat_text_latin_library/" + f, errors="ignore").read().split()) if w]
    pickle.dump(ref, open(p, "wb")); return ref
