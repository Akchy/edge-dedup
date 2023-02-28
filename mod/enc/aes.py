from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import codecs

def get_new_aes(key, iv):
    return AES.new(key, AES.MODE_CBC, iv)


def aes_encrypt_file(key, iv, in_folder, out_folder,file_name, output_file_name ='N'):
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    if output_file_name != 'N':
        out_file = out_folder+output_file_name
    else:
        out_file = out_folder+file_name
    in_file = in_folder+file_name
    # Create a new AES cipher
    cipher = get_new_aes(key, iv)

    # Read the input file and encrypt its contents
    with open(in_file, 'rb') as f:
        plaintext = f.read()
    padding_length = 16 - (len(plaintext) % 16)
    plaintext += bytes([padding_length]) * padding_length
    ciphertext = cipher.encrypt(plaintext)

    # Write the ciphertext to the output file
    with open(out_file, 'wb') as f:
        f.write(ciphertext)

def aes_decrypt_file(key, iv, in_folder, out_folder, file_name, input_name='N'):
    # Create a new AES cipher
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    out_file = out_folder+file_name
    if input_name != 'N':
        in_file = in_folder+input_name
    else:
        in_file = in_folder+file_name
    cipher = get_new_aes(key, iv)

    # Read the input file and decrypt its contents
    with open(in_file, 'rb') as f:
        ciphertext = f.read()
    plaintext = cipher.decrypt(ciphertext)
    plaintext = plaintext[:-plaintext[-1]]

    # Write the plaintext to the output file
    with open(out_file, 'wb') as f:
        f.write(plaintext)

    from Crypto.Cipher import AES
import os


def aes_encrypt_byte(key, data):
    data = int_to_bytes(data)
    data = pad(data, AES.block_size)
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(data)
    return ciphertext

def aes_decrypt_byte(key, ciphertext):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = unpad(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
    return data

def int_to_bytes(i):
    return i.to_bytes((i.bit_length() + 7) // 8, 'big')
'''
key = b'N8MttkcH0rc6laYG3zZCO1mHo3hPd6izbeei/26Yu5txQ3l3ZThtQUJiQ0JTYkM5a1BGSFFOWUlWeFRkMkgrY1BiV2k2LzA3ZVA0bG5leTZxeUVJMDV2clA3dFVWUjhpWU1rSG40VUZqRGl5RWlma05Sa01jZ04rVWR0TndoRkV2VE5IT0dTak9jMHZzbXNmaFczaU9ZOWZSSUFUZ3FEY4SxTIggI+mEfk4tmPbfUxNDwCCL6h/5dHnlakBiIu98'
key1 = 11232534634633454345654567878987887
key2 = b'njWvRQl9iJiurgZNkXqdmg=='
x =aes_encrypt_byte(key2, key1)
print(x)
r = int.from_bytes(x,'big')
print(r)
p = r.to_bytes(32,'big')
print(p)
#v = aes_decrypt_byte(key2,p)
#print(int.from_bytes(v,'big'))
#'''