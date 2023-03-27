
def file_to_binary(filename):

    with open(filename,'rb') as file:
        chunk_size = 4096*8
        binary_content = ''
        
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            binary_chunk = ''.join(format(x,'08b') for x in chunk)
            binary_content += binary_chunk
    return binary_content

    '''
    with open(filename, "rb") as f:
        # Read the file as bytes
        file_bytes = f.read()
        # Convert the bytes to a binary string
        binary_string = ''.join(format(byte, '08b') for byte in file_bytes)
        return binary_string
    #'''