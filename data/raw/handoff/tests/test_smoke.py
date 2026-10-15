import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from synthetic_baseline import make_key,encode,infer_key_from_parallel,decode,run
class TestToy(unittest.TestCase):
 def test_bijection(self):
  k=make_key(1)
  self.assertEqual(len(set(k.values())),26)
 def test_parallel_positive_control(self):
  self.assertEqual(run(),1.0)
 def test_round_trip(self):
  k=make_key(2)
  s='voynich text cannot be decoded by wishful thinking'
  e=encode(s,k)
  self.assertEqual(decode(e,{v:x for x,v in k.items()}),s)
if __name__=='__main__':unittest.main()
