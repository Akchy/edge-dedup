import random
from mod.divide_files import divide_file_by_size
from mod.enc.rsa_keys import generate_keys
from mod.modulo_hash import *
from mod.cuckoo import check_cuckoo

file_tags = [ 79289504320816749656312002797686303750053270932755277852798226741834612071265]
#file_tag =  79289504320816749656312002797686303750053270932755277852798226741834612071265
prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493
file_count = 4
file_meta = 'test.txt'
user_input_folder_name = 'subs_blocks/'

def subs_upload():
    file_tag = modulo_hash_file(file_meta,prime1)

    if file_tag not in file_tags:
        return -1
    
    challenge_blocks=0
    blocks = []
    print('duplicate')
    while challenge_blocks!=3:
        num = random.randint(1,file_count)
        if num not in blocks:
            blocks.append(num)
            challenge_blocks+=1
    #send these block numbers to User
    
    file_count=divide_file_by_size(file_meta, 1024, user_input_folder_name)

    public_key, private_key = generate_keys()

    block_keys = []
    for i in blocks:
        file_name = 'block{}.bin'.format(i)
        file_path = user_input_folder_name+file_name
        mod = modulo_hash_file(file_path,prime2)
        block_keys.append(mod)
    print(block_keys)

    flag =0
    #Send the block keys to Server
    for i in blocks:
        is_avail = check_cuckoo(i)
        if not is_avail:
            flag = 1
            break
    if(flag==1):
        print('Cuckoo Filter Failed')
        return -1
    
    # Server send one time token to user encrypted in user's public key 
    