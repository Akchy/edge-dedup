import hashlib

def get_file_signature(file_path):
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Create a new SHA-256 hash object
        sha256 = hashlib.sha256()
        # Read the file in chunks
        while chunk := f.read(4096):
            # Update the hash object with each chunk
            sha256.update(chunk)
    # Get the hexadecimal representation of the hash
    file_signature = sha256.hexdigest()
    return file_signature

file_path = 'example.txt'
file_signature = get_file_signature(file_path)
print(file_signature)
