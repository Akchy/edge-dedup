import random
import bitstring

def random_num_gen():
    rand_num = random.random()
    f1 = bitstring.BitArray(float=rand_num, length=64)
    return f1.bin

