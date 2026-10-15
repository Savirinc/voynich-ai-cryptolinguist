"""Toy cipher positive control, standard library only.
NOT a Voynich decipherment, RL model, or OOD benchmark.
A seeded monoalphabetic substitution is recoverable here because the solver
is supplied a separate known-plaintext alignment. Real decipherment agents
must NOT get that alignment at test time.
"""
import random, string
ALPHABET=string.ascii_lowercase
TEXT=("the patient reads a manuscript and studies its unusual writing "
      "the patient researcher tests every hypothesis against evidence "
      "the manuscript has lines and repeated symbols but unknown meaning ")*40

def make_key(seed=17):
    a=list(ALPHABET); random.Random(seed).shuffle(a)
    return dict(zip(ALPHABET,a))

def encode(text,key): return ''.join(key.get(c,c) for c in text)

def infer_key_from_parallel(plaintext,ciphertext):
    inverse={}
    for p,c in zip(plaintext,ciphertext):
        if p in ALPHABET:
            if c in inverse and inverse[c]!=p: raise ValueError('not consistent')
            inverse[c]=p
    return inverse

def decode(ciphertext,inverse): return ''.join(inverse.get(c,c) for c in ciphertext)

def run():
    train,test=TEXT[:int(len(TEXT)*.7)],TEXT[int(len(TEXT)*.7):]
    key=make_key()
    ct_train,ct_test=encode(train,key),encode(test,key)
    recovered=infer_key_from_parallel(train,ct_train)
    output=decode(ct_test,recovered)
    accuracy=sum(a==b for a,b in zip(output,test))/len(test)
    print('TOY POSITIVE CONTROL: substitution with KNOWN plaintext alignment')
    print('characters:',len(test),'accuracy:',round(accuracy,5),'recovered letters:',len(recovered))
    assert accuracy == 1.0
    return accuracy
if __name__=='__main__':run()
