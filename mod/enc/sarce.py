from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

# define a function to generate a random AES key
def generate_key():
    return get_random_bytes(16)

# define a function to encrypt a plaintext message using an AES key and an initialization vector (IV)
def encrypt_message(key, message):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(iv + ciphertext).decode()

# define a function to decrypt a ciphertext message using an AES key and an initialization vector (IV)
def decrypt_message(key, ciphertext):
    ciphertext = base64.b64decode(ciphertext)
    iv = ciphertext[:AES.block_size]
    ciphertext = ciphertext[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()

# define a function to generate a random nonce
def generate_nonce():
    return get_random_bytes(16)

# define a function to generate a server-side key
def generate_server_key():
    return get_random_bytes(16)

# define a function to generate a client-side key using a server-side key and a nonce
def generate_client_key(server_key, nonce):
    key_hash = hashlib.sha256(server_key + nonce).digest()
    return key_hash[:16]

# define a function to encrypt a plaintext message using SARCE
def sarce_encrypt_message(key, server_key, message):
    # generate a random nonce
    nonce = generate_nonce()
    
    # generate the client key
    client_key = generate_client_key(server_key, nonce)
    
    # encrypt the message using the client key
    ciphertext = encrypt_message(client_key, message)
    
    # hash the encrypted message and nonce to generate the tag
    tag = hashlib.sha256(ciphertext.encode() + nonce).digest()
    
    # encrypt the client key using the server key
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_client_key = cipher.encrypt(pad(client_key, AES.block_size))
    # concatenate the encrypted client key, nonce, ciphertext, and tag and return as a string
    return base64.b64encode(encrypted_client_key + nonce + ciphertext.encode() + tag).decode()

# define a function to decrypt a ciphertext message using SARCE
def sarce_decrypt_message(key, server_key, ciphertext):
    ciphertext1 = base64.b64decode(ciphertext)
    # extract the encrypted client key, nonce, ciphertext, and tag
    encrypted_client_key = ciphertext1[:32]
    nonce = ciphertext1[32:48]
    ciphertext = ciphertext1[48:-32]
    tag = ciphertext1[-32:]
    #ciphertext= ciphertext.decode()
    

    # decrypt the client key using the server key
    cipher = AES.new(key, AES.MODE_ECB)
    client_key = unpad(cipher.decrypt(encrypted_client_key), AES.block_size)
    
    # generate the tag using the decrypted ciphertext and nonce
    expected_tag = hashlib.sha256(ciphertext + nonce).digest()
    
    # verify that the tag matches the expected tag
    if tag != expected_tag:
        raise ValueError("Invalid ciphertext")
    
    # decrypt the ciphertext using the client key and return the plaintext
    return decrypt_message(client_key, ciphertext.decode())


def get_rce_key(file_tag, edge_key):
    private_keys = get_random_bytes(16)
    rce_key = sarce_encrypt_message(private_keys, edge_key, str(file_tag))
    #print(rce_key)
    return rce_key