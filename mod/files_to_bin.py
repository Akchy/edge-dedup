
def file_to_binary(filename):

    with open(filename, "rb") as f:
        # Read the file as bytes
        file_bytes = f.read()
        # Convert the bytes to a binary string
        binary_string = ''.join(format(byte, '08b') for byte in file_bytes)
        return binary_string
