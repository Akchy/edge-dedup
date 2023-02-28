import db
import random
import datetime
from mod.enc.rsa_keys import rsa_encrypt
from mod.cuckoo import check_cuckoo
from mod.enc.rsa_keys import generate_keys


def check_file_tag_exists(file_tag):
    exists = db.check_file_tag(file_tag)
    return exists

def upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags, cuckoo_blocks, metadata):
    group_name = db.upload_file(file_tag, public_key, group,cipher_2,cipher_3, block_tags, cuckoo_blocks, metadata)
    return group_name


def download_from_server(file_tag, public_key):
    val = db.get_ciphers(file_tag, str(public_key))
    if val == -1 :
        return -1 #No Access
    return val
   
def check_access(file_tag, public_key):
    has_access = db.check_access(file_tag,str(public_key)) 
    if has_access:
        return False
    meta = db.get_meta(file_tag)
    metadata = meta.split(',')
    file_name,file_count = metadata
    file_count = int(file_count[:-1])
    challenge_blocks=0
    blocks = []
    while challenge_blocks!=3:
        num = random.randint(1,file_count-1)
        if num not in blocks:
            blocks.append(num)
            challenge_blocks+=1
    return blocks

def blocks_to_server_cuckoo(file_tag, block_keys, public_key):
    flag =0
    blocks_string = db.get_cuckoo_blocks(file_tag) 
    blocks = blocks_string.split('-')
    for i in block_keys:
        is_avail = check_cuckoo(blocks,i)
        if not is_avail:
            flag = 1
            break
    if(flag==1):
        print('Cuckoo Filter Failed')
        return -1

    timestamp = datetime.datetime.now().timestamp()
    string_time = str(timestamp)
    byte_time = string_time.encode()
    time_hash = rsa_encrypt(public_key,byte_time)  
    db.save_time(str(public_key), string_time)
    return time_hash

def check_time_hash(file_tag,public_key, time_val):
    val = db.get_time_hash(str(public_key))
    if val == -1:
        return -1 # No time saved for public key
    if time_val == val:
        print('User Verified')
        db.add_owner(file_tag, str(public_key))
        print('User Added')
    return 1

def save_block_vales(block_tag, file_tag):
    db.save_block_vales(block_tag, file_tag)
    

def check_block_exists(block_tag):
    val = db.check_block_exists(block_tag)
    return val

def get_block_values(file_tag):
    tag_list = db.get_block_values(file_tag)
    return tag_list

def get_file_tag_of_block(block_tag):
    file_tag_of_block = db.get_file_tag_of_block(block_tag)
    return file_tag_of_block

def get_index_of_block(block_tag,file_tag):
    block_tags_string = get_block_values(file_tag)
    block_tags = block_tags_string.split('-')
    index = block_tags.index(block_tag)
    return index