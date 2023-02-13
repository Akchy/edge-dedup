from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def aes_encrypt_file(key, iv, in_file, out_file):
    # Create a new AES cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Read the input file and encrypt its contents
    with open(in_file, 'rb') as f:
        plaintext = f.read()
    padding_length = 16 - (len(plaintext) % 16)
    plaintext += bytes([padding_length]) * padding_length
    ciphertext = cipher.encrypt(plaintext)

    # Write the ciphertext to the output file
    with open(out_file, 'wb') as f:
        f.write(ciphertext)

def aes_decrypt_file(key, iv, in_file, out_file):
    # Create a new AES cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)

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

def aes_encrypt_text(key, plaintext):
    cipher = AES.new(key, AES.MODE_CBC)
    block_size = AES.block_size
    padding_length = block_size - (len(plaintext) % block_size)
    padding = bytes([padding_length] * padding_length)
    padded_plaintext = plaintext + padding
    iv = os.urandom(block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    return (iv, ciphertext)

def aes_decrypt_text(key, iv, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    padding_length = plaintext[-1]
    return plaintext[:-padding_length]

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