import db
import random
import datetime
from mod.enc.rsa_keys import rsa_encrypt
from mod.cuckoo import check_cuckoo
from mod.enc.rsa_keys import generate_keys


def check_file_tag_exists(file_tag):
    exists = db.check_file_tag(file_tag)
    return exists

def upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags, cuckoo_blocks, metadata, is_update, old_file_tag):
    if is_update == 'N':
        db.insert_file(file_tag, public_key, group,cipher_2,cipher_3, block_tags, cuckoo_blocks, metadata)
    else:
        db.update(old_file_tag,file_tag, public_key, cipher_2,cipher_3, block_tags, cuckoo_blocks, metadata)


# def update_file(old_file_tag, new_file_tag, public_key,cipher_2,cipher_3, block_tags,cuckoo_blocks, metadata):
#     db.update(old_file_tag, new_file_tag, public_key,cipher_2,cipher_3, block_tags,cuckoo_blocks, metadata)

def download_from_server(file_tag, public_key):
    val = db.get_ciphers(file_tag, str(public_key))
    if val == '-1' :
        return '-1' #No Access
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

def blocks_to_server_cuckoo(file_tag, block_keys_str, public_key):
    flag =0
    blocks_string = db.get_cuckoo_blocks(file_tag) 
    blocks_from_db = blocks_string.split('/')
    block_keys = block_keys_str.split('/')
    for i in block_keys:
        is_avail = check_cuckoo(blocks_from_db,i)
        if not is_avail:
            flag = 1
            break
    if(flag==1):
        print('Cuckoo Filter Failed')
        return '-1'

    timestamp = datetime.datetime.now().timestamp()
    string_time = str(timestamp)
    byte_time = string_time.encode()
    li = public_key.split(',')
    n_str = li[0]
    e_str = li[1]
    n = int(n_str[10:])
    e = int(e_str[:-1])
    time_hash = rsa_encrypt(n,e,byte_time)  
    db.save_time(str(public_key), string_time)
    int_hash = int.from_bytes(time_hash,'big')
    li = str(len(time_hash))+'*'+str(int_hash)
    return li

def check_time_hash(file_tag,public_key, time_val):
    val = db.get_time_hash(str(public_key))
    if val == -1:
        return '-1' # No time saved for public key
    if time_val == val:
        print('User Verified')
        added = db.sub_upload_add_owner(file_tag, str(public_key))
        if added!= '-1':
            print('User Added')
    return '1'

def save_block_exists_if_not_exists(block_tag_list, file_tag):
    block_tags = block_tag_list.split('/')
    saved_tags_tuple = db.check_block_exists(block_tags,file_tag)
    saved_block_tags = []
    for tags in saved_tags_tuple:
        saved_block_tags.append(tags[0])
    names_list =[]
    for i in range(len(block_tags)):
        if block_tags[i] in saved_block_tags:
            name = f'block{i+1}.bin'
            names_list.append(name)
    names_list_str = '*'.join(names_list)
    return names_list_str



def get_block_values(file_tag):
    tag_list = db.get_block_values(file_tag)
    return tag_list

def get_file_tag_and_index_of_block(block_tag,file_tag):
    file_tag_of_block = db.get_file_tag_of_block(block_tag)
    block_tags_string = get_block_values(file_tag)
    block_tags = block_tags_string.split('/')
    index = block_tags.index(block_tag)
    i= index+1
    tag = file_tag_of_block
    li = [str(i),str(tag)]
    li_str = '*'.join(li)
    return li_str

def check_for_update(file_tag):
    val = db.get_latest_file_tag(file_tag)
    return val

def add_user(file_tag, public_key, new_public_key):
    val = db.add_owner(file_tag, public_key, new_public_key)
    return val

def delete_user(file_tag, public_key, new_public_key):
    val = db.delete_owner(file_tag, public_key, new_public_key)
    return val