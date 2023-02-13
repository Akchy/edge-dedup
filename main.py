from mod.rce import RCE
from mod.file_to_blocks import divide_file
from mod.modulo_hash import *
from mod.aes import *
import random
import os

primes = [
    10964498173344902552086826832284475539,
    42843564375895932971840209911533241493,
    84115950790027114771052567640916791479,
    39898082900008726311872460047796590683,
    28253300016447640096022605126525093757,
    27498296053029454496818693651348333711,
    22634980537757979234007050835060787977,
    94536311611111401814406923925165958581,
    53547542692672999988276369883938782109,
    32005207106305622966922657739562365619,
    85182951551192967268525644386779122361,
    96422552274998437718809650734202106187]

ran = random.randint(0, 11)
p = primes[ran]
# RCE Key Generation
key = RCE()
#print('\nRCE Key: '+str(key))

#Chunking of Files
divide_file('test.txt', 9) # the value 10 is not finalised, need to check.

#i=0
#MLE Keys for each block
#while i<10:


K_b = modulo_hash_file('mod_files/block0.bin',p)
#print('\nK_b: '+str(K_b)+'\n len: '+str(len(str(K_b))))

# Generate a random key and initialization vector (IV)

bytes_val = K_b.to_bytes(16, 'big')
iv = os.urandom(16) # 16 bytes for AES-128

#print('Key: '+str(bytes_val)+'\n iv: '+str(iv))
aes_encrypt_file(bytes_val, iv, 'mod_files/block0.bin', 'output.bin')
#aes_decrypt_file(bytes_val, iv, 'output.bin', 'decrypted.bin')

l,z = key
int_l = int(l,2)
l_bytes = int_l.to_bytes(16, 'big')
print("l: {l}\nl bytes: {lb} k: {k}".format(l=int_l,lb=l_bytes,k=K_b))

# Encrypt K_b
c2 = aes_encrypt_byte(l_bytes,K_b)
dec = int.from_bytes(aes_decrypt_byte(l_bytes, c2), 'big')
print('C2: {}, \nK_b: {}'.format(str(c2),str(dec)))

# XOR z and L
c3 = z ^ int_l
print('\nc3: ',c3)

dec_l = c3 ^ z
print('dec_l: ',dec_l)

