from mod.divide_files import merge_blocks
from mod.modulo_hash import *
from mod.enc.aes import *



iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92" # 16 bytes for AES-128
cipher_2= [b'\xff(\xe8m\xc8C\x95\xc9\x894o\xbd\xca\xa2\x9b\x89\xa6\xb6T\xa87\xa1\xca\x15\xcc\xef\x12\x15G\x12Q\xaa 9\xf1QE\xbfJh"\x95k\n\\nl\xd3\x17WU\x9b\x12\x98R"\x98\xf4h;\t\xac\x83U', b'u/k\x9a\xc2,\x18\x03\xef\xf1i\xba\xa5\n\xd1\x9b\xc5\xf6J\xc6\xbfB\xfb6\x98\x08\x9b\xcfR\xfac\x14\x8f>\x92\xb2T K\xbddB2\x8c\xb8*@\xb6\x13b\xd7\xae~\xca\xb9\x97\x08\xeeI5\x03\xc7\x17\x00', b'I\xad\xbb\xbd\xd2\x17k_\xd9\x0c\x12\xf7+bD\x8bnQ@0\x12Kft\x16\xc6\xc7[\x01\x13\xda\x8d\xf0\x90\x8b>d\xaa#\xbf^\xff+\xfe\x80\xc4\x8d\x05I|\xd8\xe1\x9f\xc7\x03\xf2\xd6\xb9\xb2:\x00,\x98W']
cipher_3= 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815916104227684628118231853307557008965885231065768897046230587
edge_keys= [b'\x8c\xae\xd6\xb4\xfd\x90G\x10\x9e\xec\x9c\x97\xf6D\xbd6\xb2\xed2\x95\xacZ9\xf4\xbaRN\x8eT0\xef\x80', b'\xa8\x90\x9f-\x18`\x9b\xb9\xb1(vk\xf7\xc2\x9ax\xb9 \xd8\xba\r5r\x98\xc0`\x05\x04\xbf*\x1d\xe5', b'k\xc5\xa6\x8c\xe1\x17\xc4\x05\x7f\xad\x04\xa6\xea\xcc:\xeb\x88f\xe9\xc0\xbbz\xb4\x89\xad^\xde)$ji\x9c']
prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493
metadata = 'testing.txt'
edge_input_folder_name = 'files/edge_encrypt_blocks/'
edge_output_folder_name = 'files/edge_decrypt_blocks/'
user_output_folder_name = 'files/dencrypt_blocks/'
#derive file count from metadata
file_count = 4
#'''
#Edge Decrypt Code
for i in range (1,file_count):
    #bytes_K = cipher2[i-1]^prime2
    file_name = 'block{}.bin'.format(i)
    aes_decrypt_file(edge_keys[i-1], iv, edge_input_folder_name, edge_output_folder_name,file_name)
#'''
#Pass the edge decrypted files to user 

int_rce_key = cipher_3 ^prime2
rce_key = int_rce_key.to_bytes(24,'big')
for i in range (1,file_count):
    block_key = aes_decrypt_byte(rce_key,cipher_2[i-1])
    file_name = 'block{}.bin'.format(i)
    aes_decrypt_file(block_key, iv, edge_output_folder_name, user_output_folder_name,file_name)

merge_blocks(user_output_folder_name,metadata)
print('File downloaded and saved under the name: ',metadata)
#'''