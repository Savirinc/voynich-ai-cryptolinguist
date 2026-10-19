for seed in 2 3 4; do for m in real shuf rugg_rep self_citation_rep; do
  /Users/arhampartapjain/voynich-ai-cryptolinguist/.venv/bin/python cmp_pipe.py 0.6 28000 4 3 $m $seed 2>&1 | grep -v "^truth\|^ref\|^decoded"
done; done
