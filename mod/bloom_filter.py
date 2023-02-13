import hashlib
import bitarray

class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray.bitarray(size)
        self.bit_array.setall(0)

    def add(self, item):
        for seed in range(self.hash_count):
            result = int(hashlib.sha1(item.encode()).hexdigest(), 16)
            index = result % self.size
            self.bit_array[index] = 1

    def check(self, item):
        for seed in range(self.hash_count):
            result = int(hashlib.sha1(item.encode()).hexdigest(), 16)
            index = result % self.size
            if self.bit_array[index] == 0:
                return False
        return True
