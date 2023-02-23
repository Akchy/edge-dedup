from mod.enc.sarce import get_rce_key
#from Crypto.Util.number import getPrime,getStrongPrime
from mod.divide_files import divide_file_by_size, merge_blocks
from Crypto.Random import get_random_bytes
from mod.modulo_hash import *
from mod.enc.aes import *

prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493

user_input_folder_name = 'files/blocks/'
user_output_folder_name = 'files/encrypt_blocks/'
edge_input_folder_name = 'files/encrypt_blocks/'
edge_output_folder_name = 'files/edge_encrypt_blocks/'
file_meta = 'test.txt'

# RCE Key Generation
key = get_rce_key() #change the RCE method to sarce

output_folder = 'files/blocks'
#print('\nRCE Key: '+str(key))

#Chunking of Files
file_count=divide_file_by_size(file_meta, 1024, output_folder)

#i=0
#MLE Keys for each block
#while i<10:
block_keys = []
for i in range (1,file_count):
    file_name = 'block{}.bin'.format(i)
    file_path = user_input_folder_name+file_name
    mod = modulo_hash_file(file_path,prime1)
    block_keys.append(mod)


#print('block_keys: {} \nlen: {}'.format(block_keys, len(str(block_keys))))
#print('\nblock_keys: '+str(block_keys)+'\n len: '+str(len(str(block_keys))))

# Generate a random key and initialization vector (IV)

cipher2=[]
iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92" # 16 bytes for AES-128
for i in range (1,file_count):
    bytes_K = block_keys[i-1].to_bytes(32, 'big')
    file_name = 'block{}.bin'.format(i)
    aes_encrypt_file(bytes_K, iv, user_input_folder_name, user_output_folder_name,file_name)
    cipher2.append(block_keys[i-1]^prime2)

#Save Key from above encryption.


#Edge will encrypt each block again and save the Key in the edge node along with hash of the block
edge_iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
edge_keys=[]
for i in range (1,file_count):
    edge_bytes_K = get_random_bytes(32)
    edge_keys.append(edge_bytes_K)
    file_name = 'block{}.bin'.format(i)
    aes_encrypt_file(edge_bytes_K, edge_iv, edge_input_folder_name, edge_output_folder_name,file_name)
    file_path = edge_output_folder_name+file_name
    block_tag = modulo_hash_file(file_path,prime1)
    
with open('cred.txt','w') as file:
    file.write('cipher: {} \nedge_keys: {}'.format(cipher2,edge_keys))
#Save the block tag in edge.


#Decrypt Code

'''
for i in range (1,file_count):
    #bytes_K = block_keys[i-1].to_bytes(32, 'big')
    input_folder_name = 'encrypt_blocks/'
    enc_output_folder_name = 'decrypt_blocks/'
    file_name = 'block{}.bin'.format(i)
    aes_decrypt_file(edge_keys[i-1], edge_iv, input_folder_name, enc_output_folder_name,file_name)
#'''
