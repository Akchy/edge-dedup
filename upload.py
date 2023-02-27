from mod.enc.sarce import get_rce_key
#from Crypto.Util.number import getPrime,getStrongPrime
from mod.divide_files import divide_file_by_size
from mod.modulo_hash import *
from mod.enc.aes import *
from mod.enc.rsa_keys import generate_keys


def upload_file(file_name, old_file_tag='', is_update=False):
    prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
    prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493
    if not os.path.exists('files'):
        os.mkdir('files')
    if not os.path.exists('datas'):
        os.mkdir('datas')
    user_input_folder_name = 'files/blocks/'
    user_output_folder_name = 'files/encrypt_blocks/'
    edge_input_folder_name = 'files/encrypt_blocks/'
    edge_output_folder_name = 'files/edge_encrypt_blocks/'
   
    public_key, private_key = generate_keys()


    file_tag = modulo_hash_file(file_name,prime1)
    # RCE Key Generation
    rce_key = get_rce_key(file_tag) #change the RCE method to sarce
    rce_key = bytes(rce_key[0:24],'utf-8')
    #print('\nRCE Key: ',rce_key)
    
    #Chunking of Files
    file_count=divide_file_by_size(file_name, 1024, user_input_folder_name)

    block_keys = []
    #block_tokens = []
    cipher_2 = []
    iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
    for i in range (1,file_count):
        block_name = 'block{}.bin'.format(i)
        block_path = user_input_folder_name+block_name
        mod = modulo_hash_file(block_path,prime1)
        block_keys.append(mod)
        bytes_K = mod.to_bytes(32, 'big')
        aes_encrypt_file(bytes_K, iv, user_input_folder_name, user_output_folder_name,block_name)
        cipher_2.append(aes_encrypt_byte(rce_key,mod))
        #wrong place
        #block_token = modulo_hash_file(block_path,prime2)
        #block_tokens.append(block_token)

    int_rce_key = int.from_bytes(rce_key,'big')
    cipher_3 = int_rce_key ^ prime2

    # Save Cipher_2 and Cipher_3 in a file

    # Saving User's Public and Private keys in a file.
    with open('datas/rsa.txt','w+') as file:
        file.write('public= {} \nprivate= {}'.format(public_key,private_key))

    with open('datas/file_tag.txt', 'a+') as file:
        file.write('file_tag= {}'.format(file_tag))

    with open('datas/metadata.txt', 'a+') as file:
        file.write('\nfile_name= {}\nfile_count= {}'.format(file_name, file_count))

    with open('datas/ciphers.txt', 'a+') as file:
        file.write('cipher_2= {}\ncipher_3= {}'.format(cipher_2,cipher_3))

    #-----------------------------------------------------------------------------------#

    #Edge will encrypt each block again and save the Key in the edge node along with hash of the block
    edge_iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
    edge_keys=[]
    block_tokens=[]
    for i in range (1,file_count):
        edge_bytes_K = os.urandom(32)
        edge_keys.append(edge_bytes_K)
        block_name = 'block{}.bin'.format(i)
        aes_encrypt_file(edge_bytes_K, edge_iv, edge_input_folder_name, edge_output_folder_name,block_name)
        block_path = edge_output_folder_name+block_name
        mod = modulo_hash_file(block_path,prime1)
        block_tokens.append(mod)
        #Save the block tag in edge.

    # Saving Cipher2 and Edge Keys in a file.    
    with open('datas/cred.txt','w+') as file:
        file.write('block_tokens= {} \nedge_keys= {}'.format(block_tokens,edge_keys))

    #Decrypt Code

    '''
    for i in range (1,file_count):
        #bytes_K = block_keys[i-1].to_bytes(32, 'big')
        input_folder_name = 'encrypt_blocks/'
        enc_output_folder_name = 'decrypt_blocks/'
        file_name = 'block{}.bin'.format(i)
        aes_decrypt_file(edge_keys[i-1], edge_iv, input_folder_name, enc_output_folder_name,file_name)
    #'''


upload_file('test.txt')