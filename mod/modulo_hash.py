import hashlib

def modulo_hash_file(file_path, modulus):
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Read the file content
        file_content = f.read()
        # Create a new SHA-256 hash object
        sha256 = hashlib.sha256()
        # Update the hash object with the file content
        sha256.update(file_content)
        # Get the hexadecimal representation of the hash
        file_hash = sha256.hexdigest()
        # Convert the hash to an integer
        int_hash = int(file_hash, 16)
        # Convert the int to a binary
        bin_val_hash = int(bin(int_hash)[2:])
        # Apply the modulo operation to the hash
        modulo_hash = bin_val_hash % modulus
    return modulo_hash
