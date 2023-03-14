import rsa
from Crypto.Util.number import getStrongPrime

def generate_keys():
# Generate a pair of RSA public and private keys
    (public_key, private_key) = rsa.newkeys(1048)

    # Print the public key
    #Public = n,e , Private = n,e,d,p,q
    return (public_key, private_key)

def rsa_encrypt(n,e, message):
    ciphertext = rsa.encrypt(message, rsa.PublicKey(n,e))
    return ciphertext

def rsa_decypt(private_key, ciphertext):
    plaintext = rsa.decrypt(ciphertext, private_key)
    return plaintext.decode()

def rsa_pem_format(public_key, privte_key):

    # Convert the keys to PEM format for easy storage
    private_key_pem = privte_key.save_pkcs1().decode()
    public_key_pem = rsa.PublicKey(public_key.n, public_key.e).save_pkcs1().decode()
    return (private_key_pem, public_key_pem)
