"""Voynich experiment 008: reproducible cross-language corpus comparison harness.

Usage:
  python voynich_experiment_008.py
  python voynich_experiment_008.py --corpora-dir /path/to/plain-text-corpora

Text corpora expected as UTF-8 files, e.g. middle_english.txt, medieval_latin.txt,
classical_sanskrit_iast.txt, middle_persian.txt. Unprovided languages are NEVER ranked.
WARNING: naive Romanization / EVA units do not map one-to-one to manuscript glyphs.
"""
import argparse,collections,json,math,re,random
from pathlib import Path
BASE=Path(__file__).resolve().parent
SOURCES=['voynich_f1r_sample.txt','voynich_heldout_f1v_f2r.txt','voynich_f3r_reference.txt']
def tokens(s, voy=False):
    result=[]
    for line in s.splitlines():
        if not line.strip() or line.startswith('#'): continue
        if voy:
            line=re.sub(r'^<[^>]+>\s*','',line)
            # '<->' explicitly denotes a line boundary; do NOT concatenate across it.
            line=line.replace('<->','.')
            raw=re.split(r'[.,\s]+',line)
            result.extend(w for w in raw if re.fullmatch('[a-z]+',w))
        else:
            result.extend(re.findall(r'[^\W\d_]+',line.lower(),re.UNICODE))
    return result
def countpair(toks):
    # Word boundaries respected; do not mix across words.
    return collections.Counter((a,b) for t in toks for a,b in zip(t,t[1:])),collections.Counter(a for t in toks for a in t[:-1])
def entropy(vals):
    s=sum(vals)
    return -sum((v/s)*math.log2(v/s) for v in vals if v) if s else None
def features(toks):
    chars=collections.Counter(''.join(toks)); pairs,prev=countpair(toks)
    N=sum(chars.values()); pairN=sum(pairs.values())
    H1=entropy(chars.values())
    H2=-sum(v/pairN*math.log2(v/prev[a]) for (a,b),v in pairs.items()) if pairN else None
    vc=collections.Counter(toks); lengths=collections.Counter(map(len,toks))
    return {'tokens':len(toks),'characters':N,'vocabulary':len(vc),'types_per_token':round(len(vc)/len(toks),4) if toks else None,
            'mean_word_length':round(N/len(toks),4) if toks else None,
            'char_entropy':round(H1,4) if H1 is not None else None,
            'within_word_conditional_entropy':round(H2,4) if H2 is not None else None,
            'top_words':vc.most_common(12),'top_characters':chars.most_common(12),
            'word_length_histogram':dict(sorted(lengths.items()))}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--corpora-dir',type=Path);ap.add_argument('--output',type=Path,default=BASE/'voynich_experiment_008_results.json');args=ap.parse_args()
    words=[]; by_source={}
    for source in SOURCES:
        toks=tokens((BASE/source).read_text(),voy=True)
        by_source[source]=features(toks)
        words.extend(toks)
    # Note deliberately no English example passage in the corpus comparisons.
    corpus={}
    if args.corpora_dir:
        for p in sorted(args.corpora_dir.glob('*.txt')):
            corpus[p.stem]=features(tokens(p.read_text(encoding='utf-8')))
    result={'source_samples':SOURCES,'method':'Within-word adjacent unit entropy; strict plain a-z EVA tokens only; no uncertain glyphs or markup retained.',
            'voynich_all_samples':features(words),'voynich_by_source':by_source,
            'reference_corpora':corpus,'comparison_complete':bool(corpus),
            'caveats':['No legitimate language-family ranking without historical corpora and comparable transliteration.',
                       'Unequal corpus sizes and genres bias lexical measures; match by words and bootstrap in later runs.',
                       'EVA multigraphs and accents/romanization can bias entropy; segment and normalize.',
                       'Short early Currier A samples are not manuscript-wide evidence.',
                       'Statistical resemblance cannot identify the plaintext language.']}
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps({
      'sample_metrics':result['voynich_all_samples'],'reference_corpora_loaded':list(corpus),'complete':result['comparison_complete']},indent=2))
if __name__=='__main__':main()
