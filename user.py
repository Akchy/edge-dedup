# Here's the code for user
import edge
import server
from mod.enc.aes import *
from mod.modulo_hash import *
from mod.enc.sarce import get_rce_key
from mod.divide_files import merge_blocks
from mod.enc.rsa_keys import generate_keys
from mod.divide_files import divide_file_by_size

prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493

user_input_folder_name = 'files/blocks/'
user_output_folder_name = 'files/encrypt_blocks/'
user_down_input_folder_name = 'files/edge_decrypt_blocks/'
user_down_output_folder_name = 'files/dencrypt_blocks/'

iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
if not os.path.exists('files'):
        os.mkdir('files')
if not os.path.exists('datas'):
        os.mkdir('datas')



def user_upload(file_name, group):
    file_tag = get_file_tag(file_name)
    # RCE Key Generation
    edge_rce_key = edge.get_edge_rce_key()
    str_rce_key = get_rce_key(file_tag,edge_rce_key)
    rce_key = bytes(str_rce_key[0:24],'utf-8')
    file_exists = server.check_file_tag_exists(file_tag)
    if file_exists == True:
        print('duplicate')
    else:
        public_key, private_key = generate_keys()
        file_count,cipher_2,cipher_3=encrypt_blocks(file_name, file_tag, rce_key, public_key, private_key)
        metadata = [file_name,file_count]
        cipher_2_list= '-'.join(str(c) for c in cipher_2)
        group_name = edge.upload_to_edge(file_tag, str(public_key), group, file_count,cipher_2_list,str(cipher_3), str(metadata))

        #save group name in a file
        with open('datas/group_name.txt', 'a+') as file:
            file.write('\n\ngroup_name= {}'.format(group_name))

def get_file_tag(file_name):
    return modulo_hash_file(file_name,prime1)

def encrypt_blocks(file_name, file_tag, rce_key, public_key, private_key):
    file_count=divide_file_by_size(file_name, 1024, user_input_folder_name)
    block_keys = []
    #block_tokens = []
    cipher_2 = []
    for i in range (1,file_count):
        block_name = 'block{}.bin'.format(i)
        block_path = user_input_folder_name+block_name
        mod = modulo_hash_file(block_path,prime1)
        block_keys.append(mod)
        bytes_K = mod.to_bytes(32, 'big')
        aes_encrypt_file(bytes_K, iv, user_input_folder_name, user_output_folder_name,block_name)
        print('\nblock Key: ',bytes_K)
        bytes_cipher = aes_encrypt_byte(rce_key,mod)
        int_cipher = int.from_bytes(bytes_cipher,'big')
        cipher_2.append(int_cipher)

    int_rce_key = int.from_bytes(rce_key,'big')
    cipher_3 = int_rce_key ^ prime2
    
    # Saving User's Public and Private keys in a file.
    with open('datas/rsa.txt','w+') as file:
        file.write('\n\npublic= {} \nprivate= {}'.format(public_key,private_key))

    with open('datas/file_tag.txt', 'a+') as file:
        file.write('\n\nfile_tag= {}'.format(file_tag))

    with open('datas/metadata.txt', 'a+') as file:
        file.write('\n\nfile_name= {}\nfile_count= {}'.format(file_name, file_count))

    with open('datas/ciphers.txt', 'a+') as file:
        file.write('\n\ncipher_2= {}\ncipher_3= {}'.format(cipher_2,cipher_3))

    return file_count, cipher_2, cipher_3

def user_download(file_name,public_key):
    file_tag = get_file_tag(file_name)
    val =edge.download_from_edge(file_tag, public_key)
    if val == -1:
        print('No Access to the file')
        return -1
    cipher_2_list, cipher_3, metadata =val
    save_file_name, file_count = metadata
    save_file_name =save_file_name[2:-1]
    cipher_2_str = cipher_2_list.split('-')
    file_count = int(file_count[:-1])
    cipher_3_int = int(cipher_3)
    int_rce_key = cipher_3_int ^prime2
    rce_key = int_rce_key.to_bytes(24,'big')
    for i in range (1,file_count):
        cipher_2_int = int(cipher_2_str[i-1])
        byte_cipher = cipher_2_int.to_bytes(64,'big')
        block_key = aes_decrypt_byte(rce_key,byte_cipher)
        file_name = 'block{}.bin'.format(i)
        aes_decrypt_file(block_key, iv, user_down_input_folder_name, user_down_output_folder_name,file_name)

    merge_blocks(user_down_output_folder_name,save_file_name)
    print('File downloaded and saved under the name: ',save_file_name)
    return 1

#user_upload('test.txt','N')
public_key = 'PublicKey(1619750136252618332977235896406521010807545517612785245212451483502410574525825995344209832503413765595553218797211650165668796624501025356465915373792919645936327492224490288645578575138223278878781813799762886037191557934865815503565013998614220110374116025960745945204394432266977381294688936349494087274295987083, 65537)'
user_download('test1.txt', public_key)

'''
b'\xa6\xa5~\xc0\xd5B2\xb4\xaa\xdd\xf49"\xb2\x16\x0e\xaa?\xc5~\x81@M\xd3\\G[\x8f\xc4\x92\xd82\xbd\x98yX=1\xaf\xf2\x96?\xe5QB\xc1\x08\x8c?\x18\x883d\xb7\xb4\x99}OL|\xdc\xc3\r\x07'
b'\xa6\xa5~\xc0\xd5B2\xb4\xaa\xdd\xf49"\xb2\x16\x0e\xaa?\xc5~\x81@M\xd3\\G[\x8f\xc4\x92\xd82\xbd\x98yX=1\xaf\xf2\x96?\xe5QB\xc1\x08\x8c?\x18\x883d\xb7\xb4\x99}OL|\xdc\xc3\r\x07'
'''