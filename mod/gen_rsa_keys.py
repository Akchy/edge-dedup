import rsa

def generate_keys():
# Generate a pair of RSA public and private keys
    (public_key, private_key) = rsa.newkeys(2048)

    # Print the public key
    #Public = n,e , Private = n,e,d,p,q
    return (private_key.n,private_key.e,private_key.d)
