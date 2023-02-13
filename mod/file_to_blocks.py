import os

def divide_file(file_path, n):
    block_size = os.path.getsize(file_path) // n
    with open(file_path, 'rb') as f:
        for i in range(n):
            block = f.read(block_size)
            with open(f'mod_files/block{i}.bin', 'wb') as block_file:
                block_file.write(block)
            if i == n-1:
                block = f.read()
                with open(f'mod_files/block{i+1}.bin', 'wb') as block_file:
                    block_file.write(block)
