import os

def divide_file_by_count(file_path, n):
    block_size = os.path.getsize(file_path) // n
    with open(file_path, 'rb') as f:
        for i in range(n):
            block = f.read(block_size)
            with open(f'blocks/block{i}.bin', 'wb') as block_file:
                block_file.write(block)
            if i == n-1:
                block = f.read()
                with open(f'blocks/block{i+1}.bin', 'wb') as block_file:
                    block_file.write(block)

def divide_file_by_size(filename, block_size, output_folder):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    with open(filename, 'rb') as f:
        block_num = 1
        while True:
            block = f.read(block_size)
            if not block:
                break
            output_filename = os.path.join(output_folder, f'block{block_num}.bin')
            with open(output_filename, 'wb') as out_file:
                out_file.write(block)
            block_num += 1
    return block_num

def merge_blocks(input_folder, output_filename):
    with open(output_filename, 'wb') as out_file:
        block_num = 1
        while True:
            input_filename = os.path.join(input_folder, f'block{block_num}.bin')
            if not os.path.exists(input_filename):
                break
            with open(input_filename, 'rb') as in_file:
                block = in_file.read()
                out_file.write(block)
            block_num += 1


