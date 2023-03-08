import server
import mod.enc.aes as AES
from mod.modulo_hash import *
from Crypto.Random import get_random_bytes

edge_input_folder_name = 'files/encrypt_blocks/'
edge_output_folder_name = 'files/edge_encrypt_blocks/'
edge_down_input_folder_name = 'files/edge_encrypt_blocks/'
edge_output_down_folder_name = 'files/edge_decrypt_blocks/'


prime2 = 11037229919296391044771832604060314898870002775346764076594975490923595002795272111869578867022764684137991653602919487206273710450289426260391664067192117
iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
edge_key = b'\xe8\xab\xad\xb9@Z<f\xd2\xa6\x96\xbb\xfe\xbb2\x14\x17\xea\x0f\xb4\xffQOr\xc8R\xfcT;j\xe7V'

def get_edge_rce_key():
    return get_random_bytes(16)

def upload_to_edge(file_tag, public_key, group, file_count,cipher_2,cipher_3, cuckoo_blocks, metadata, is_update, old_file_tag):
    block_tags=[]
    for i in range (1,file_count):
        o_file_name = str(file_tag)+'_{}.bin'.format(i)
        block_name = 'block{}.bin'.format(i)
        AES.aes_encrypt_file(edge_key, iv, edge_input_folder_name, edge_output_folder_name,block_name,o_file_name)

        block_path = edge_output_folder_name+o_file_name
        mod = modulo_hash_file(block_path,prime2)
        block_tags.append(mod)
        #Comm: Get block exists
        val = server.check_block_exists(str(mod))
        if not val:
            #Comm: Save block 
            server.save_block_vales(str(mod), file_tag)
            #Send only the unique ones.

    block_tags_list= '-'.join(str(b) for b in block_tags)
    #Comm: Send file to server
    group_name = server.upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags_list, cuckoo_blocks, metadata, is_update, old_file_tag)

    return group_name

def download_from_edge(file_tag, public_key):
    #Comm: Get file
    val = server.download_from_server(file_tag, public_key)
    if val == -1:
        return -1 # No Access
    cipher_2, cipher_3, block_tags, metadata = val
    metadata = metadata.split(',')
    _, file_count = metadata
    file_count = file_count[:-1]
    tag_list_string= block_tags
    tag_list = tag_list_string.split('-')
    for i in range (1,int(file_count)):
        block_name = 'block{}.bin'.format(i)
        block_tag = tag_list[i-1]
        #Comm: Get file tag
        file_tag_of_block = server.get_file_tag_of_block(block_tag) #define
        if file_tag != file_tag_of_block:
            #Comm: get index of block
            index = server.get_index_of_block(block_tag,file_tag)+1 #define
            block_suffix = file_tag_of_block
            #fetch block
        else:
            index = i
            block_suffix = file_tag
        input_file_name = str(block_suffix)+'_{}.bin'.format(index)
        #Comm: Send file to User
        AES.aes_decrypt_file(edge_key, iv, edge_down_input_folder_name, edge_output_down_folder_name,block_name,input_file_name)
        
    return cipher_2, cipher_3, metadata

#Below are the functions which passes or retrieves value to or from server

def check_file_tag_exists_server(file_tag):
    file_exists = server.check_file_tag_exists(file_tag)
    return file_exists

def check_access_server(file_tag,public_key):
    val = server.check_access(file_tag,public_key)
    return val

def blocks_to_server_cuckoo_server(file_tag, block_keys, public_key):
    val = server.blocks_to_server_cuckoo(file_tag,block_keys, public_key)
    return val

def check_time_hash_server(file_tag, public_key, time_dec):
    val = server.check_time_hash(file_tag, public_key, time_dec)
    return val

def check_fo_update_server(file_tag):
    val = server.check_fo_update_server(file_tag)
    return val

def add_user_server(file_tag, public_key, new_public_key):
    val = server.add_user_server(file_tag, public_key, new_public_key)
    return val

def delete_user_server(file_tag, public_key, new_public_key):
    val = server.delete_user_server(file_tag, public_key, new_public_key)
    return val