from funcs.mod.files_to_bin import *

def modulo_hash_file(filepath, modulus):
    file_bin = file_to_binary(filepath)
    #print('file bin: ',file_bin)
    #convert binary string to int
    int_val = int(file_bin,2)
    #print('int_val',int_val)
    modulo_hash = int_val % modulus
    #print('mod hash xx: ',modulo_hash)
    return modulo_hash