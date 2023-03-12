import socket 
import threading
import server
import mod.enc.aes as AES
from mod.modulo_hash import *
from Crypto.Random import get_random_bytes

HEADER = 64
PORT = 5050
EDGE = socket.gethostname()
EDGE_ADDR = ('', PORT)
SERVER_ADDR = ('10.0.0.3', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"

edge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
edge_socket.bind(EDGE_ADDR)


edge_input_folder_name = 'files/encrypt_blocks/'
edge_output_folder_name = 'files/edge_encrypt_blocks/'
edge_down_input_folder_name = 'files/edge_encrypt_blocks/'
edge_output_down_folder_name = 'files/edge_decrypt_blocks/'


prime2 = 11037229919296391044771832604060314898870002775346764076594975490923595002795272111869578867022764684137991653602919487206273710450289426260391664067192117
iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
edge_key = b'\xe8\xab\xad\xb9@Z<f\xd2\xa6\x96\xbb\xfe\xbb2\x14\x17\xea\x0f\xb4\xffQOr\xc8R\xfcT;j\xe7V'


def handle_user(conn, addr):
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            print(f'len: {msg_length}')
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            str_to_list = msg.split('-')
            command = str_to_list[0]
            val = str_to_list[1]
            print(f'command: {command}, val: {val}')        
            value = check_command(command,val,msg,conn)
            conn.send(f"return-{value}".encode(FORMAT))
    conn.close()


def check_command(key,arg,msg,conn):
    val = 1
    match key:
        case 'get_edge_rce_key':
            b = get_edge_rce_key()
            int_byte = int.from_bytes(b,'big')
            val=str(int_byte)
        case 'upload_to_edge':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            group = lists[2]
            file_count = lists[3]
            cipher_2 = lists[4]
            cipher_3 = lists[5]
            cuckoo_blocks = lists[6]
            metadata = lists[7]
            is_update = lists[8]
            old_file_tag = lists[9]
            #upload_to_edge(file_tag, public_key, group, file_count,cipher_2,cipher_3, cuckoo_blocks, metadata, is_update, old_file_tag)
            
        case 'check_file_tag_exists':
            val = send_text_server(message=msg)
        case 'check_access':
            val = send_text_server(message=msg)
        case 'large_text':
            v = large_text(int(arg), conn)
            #val =check_command(v)
        case 'key':
            print(f'val: {arg}')
        case 'tag':
            val = send_text_server(msg)
        case 'send_file':
            get_file(arg, conn)
            send_file_to_server(arg)
        case 'get_file':
            get_file_from_server(arg)
            send_file(arg, conn)
        case default:
            print("something")
    if val !=1:
        return val
 
def large_text(count,conn):
    i=0
    large = ''
    while i<count:
        i+=1
        data = conn.recv(1024).decode(FORMAT)
        large +=data
        print(f'x: {large}')
    print('hola')
    '''
    #Working properly
    data = conn.recv(1024).decode(FORMAT)
    large = data
    print(f'x: {large}')
    while data:
        data = conn.recv(1024).decode(FORMAT)
        large +=data
        print(f'x: {large}')
    conn.send(f'large_text-received'.encode(FORMAT))
    return large
    ''
    i=0
    str = ''
    while True:
        i+=1
        msg_length = conn.recv(HEADER).decode(FORMAT)
        print(f'msg len: {msg_length}')
        msg_length = int(msg_length)
        x = conn.recv(msg_length).decode(FORMAT)
        print(f'x: {x}: \nloop count: {i} \ncount: {count}')
        str += x
        if i==count:
            break
    print(f'str: {str}')
    #'''

def send_text_server(message):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDR)
    __send_to_server(message,server_socket)
    __send_to_server(DISCONNECT_MESSAGE,server_socket)
    list_string =server_socket.recv(2048).decode(FORMAT)
    server_socket.close()
    print(f'return: {list_string}')
    list = list_string.split('-')
    val = list[1]
    return val

def get_file(filename, file_conn): 
    with open(filename, 'wb') as f:
        data = file_conn.recv(1024)
        while data:
            f.write(data)
            data = file_conn.recv(1024) 

def send_file(filename, file_conn):
    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            file_conn.send(data)
            data = f.read(1024)


def send_file_to_server(filename):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDR)
    send_file_name_list = ['send_file',filename]
    send_file_name_string = '-'.join(send_file_name_list)
    __send_to_server(send_file_name_string,server_socket)

    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            server_socket.send(data)
            data = f.read(1024)
    server_socket.close()

def get_file_from_server(filename):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDR)
    get_file_name_list = ['get_file', filename]
    get_file_name_string = '-'.join(get_file_name_list)
    __send_to_server(get_file_name_string,server_socket)
    with open(filename, 'wb') as f:
        data = server_socket.recv(1024)
        while data:
            f.write(data)
            data = server_socket.recv(1024) 
    server_socket.close()

def __send_to_server(msg,server_socket):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server_socket.send(send_length)
    server_socket.send(message)

def start():
    edge_socket.listen()
    print(f"[LISTENING] Edge is listening on {EDGE}")
    while True:
        conn, addr = edge_socket.accept()
        thread = threading.Thread(target=handle_user, args=(conn, addr))
        thread.start()

def get_edge_rce_key():
    return get_random_bytes(16)


def upload_to_edge(file_tag, public_key, group, file_count,cipher_2,cipher_3, cuckoo_blocks, metadata, is_update, old_file_tag):
    block_tags=[]
    for i in range (1,file_count):
        o_file_name = str(file_tag)+'_{}.bin'.format(i)
        block_name = 'block{}.bin'.format(i)
        AES.aes_encrypt_file(edge_key, iv, edge_input_folder_name, edge_output_folder_name,block_name,o_file_name)

        block_path = edge_output_folder_name+o_file_name
        mod = modulo_hash_file(block_path,prime2)
        block_tags.append(mod)
        #Comm: Get block exists
        command = 'check_block_exists'
        arg = str(mod)
        #val = comm.send_text(command,arg)
        val = server.check_block_exists(str(mod))
        if not val:
            #Comm: Save block 
            command = 'save_block_vales'
            l = [str(mod),str(file_tag)]
            s = '-'.join(l)
            arg = s
            #val = comm.send_text(command,arg)
            server.save_block_vales(str(mod), file_tag)
            #Send only the unique ones.

    block_tags_list= '-'.join(str(b) for b in block_tags)
    #Comm: Send file to server
    group_name = server.upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags_list, cuckoo_blocks, metadata, is_update, old_file_tag)

def download_from_edge(file_tag, public_key):
    #Comm: Get file
    val = server.download_from_server(file_tag, public_key)
    if val == -1:
        return -1 # No Access
    cipher_2, cipher_3, block_tags, metadata = val
    metadata = metadata.split(',')
    _, file_count = metadata
    file_count = file_count[:-1]
    tag_list_string= block_tags
    tag_list = tag_list_string.split('-')
    for i in range (1,int(file_count)):
        block_name = 'block{}.bin'.format(i)
        block_tag = tag_list[i-1]
        #Comm: Get file tag
        command = 'get_file_tag_of_block'
        arg = block_tag
        #file_tag_of_block = comm.send_text(command,arg)
        file_tag_of_block = server.get_file_tag_of_block(block_tag) #define
        if file_tag != file_tag_of_block:
            #Comm: get index of block
            command = 'get_index_of_block'
            l = [block_tag,file_tag]
            s = '-'.join(l)
            arg = s
            #index = comm.send_text(command,arg)
            index = server.get_index_of_block(block_tag,file_tag)+1 #define
            block_suffix = file_tag_of_block
            #fetch block
        else:
            index = i
            block_suffix = file_tag
        input_file_name = str(block_suffix)+'_{}.bin'.format(index)
        #Comm: Send file to User
        AES.aes_decrypt_file(edge_key, iv, edge_down_input_folder_name, edge_output_down_folder_name,block_name,input_file_name)
        
    return cipher_2, cipher_3, metadata


start()