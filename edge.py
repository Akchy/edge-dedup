import os
import server
import mod.enc.aes as AES
from mod.modulo_hash import *
from Crypto.Random import get_random_bytes

edge_input_folder_name = 'files/encrypt_blocks/'
edge_output_folder_name = 'files/edge_encrypt_blocks/'
edge_down_input_folder_name = 'files/edge_encrypt_blocks/'
edge_output_down_folder_name = 'files/edge_decrypt_blocks/'

if not os.path.exists('datas'):
        os.mkdir('datas')
prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"

#update while downloading
edge_keys= [b'O\xed\xaf\x9f\x89\x172\xae\tTw\xb7\x11\x99\x01a\xd9i\xcc\x1cA\xc6\xcd\xc1\x98\xee\xad\xf06w\x1a\xeb', b'\x98\xe6v\x89(j\xc5\xf6/\xdc"\x14\x90\x11r\xdd\x16d\xac\x96\x9f\xff\xf9\x19\xbe^\xc7\xab(\x10J\x84', b"i#.h\xe8\xca'\x89\x16\x9b\x82\xfc\xc5:\xfd\xd6\x84\x05\xcc\x04\x95\x9a\xdb\x1a\xff\x1a2#E\xa4=\xa9"]

def get_edge_rce_key():
    return get_random_bytes(16)

def upload_to_edge(file_tag, public_key, group, file_count,cipher_2,cipher_3, metadata):
    edge_keys=[]
    block_tokens=[]
    for i in range (1,file_count):
        edge_bytes_K = os.urandom(32)
        edge_keys.append(edge_bytes_K)
        block_name = 'block{}.bin'.format(i)
        AES.aes_encrypt_file(edge_bytes_K, iv, edge_input_folder_name, edge_output_folder_name,block_name)
        block_path = edge_output_folder_name+block_name
        mod = modulo_hash_file(block_path,prime1)
        block_tokens.append(mod)
        #Save the block tag in edge.

    block_level_dedup()
    group_name = server.upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, metadata)

    # Saving Cipher2 and Edge Keys in a file.    
    with open('datas/cred.txt','w+') as file:
        file.write('block_tokens= {} \nedge_keys= {}'.format(block_tokens,edge_keys))

    return group_name

def block_level_dedup():
    return 1

def download_from_edge(file_tag, public_key):
    val = server.download_from_server(file_tag, public_key)
    if val == -1:
        return -1
    cipher_2, cipher_3, metadata = val
    metadata = metadata.split(',')
    _, file_count = metadata
    file_count = file_count[:-1]
    for i in range (1,int(file_count)):
    #bytes_K = cipher2[i-1]^prime2
        block_name = 'block{}.bin'.format(i)
        #edge_keys = get_edge_block_keys(file_tag)
        AES.aes_decrypt_file(edge_keys[i-1], iv, edge_down_input_folder_name, edge_output_down_folder_name,block_name)
        
    return cipher_2, cipher_3, metadata

def get_edge_block_keys(file_tag):
    return 1