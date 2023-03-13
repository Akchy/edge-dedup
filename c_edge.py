import os
import socket 
import threading
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
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            str_to_list = msg.split('-')
            command = str_to_list[0]
            val = str_to_list[1]
            print(f'command: {command}, val: {val}')        
            value = check_command(command,val,msg,conn)
            if value != 'dav1sh':
                conn.send(f"return-{value}".encode(FORMAT))
    conn.close()


def check_command(key,arg,msg,conn):
    val = 'dav1sh'
    match key:
        case 'folder_share':
            get_folder(arg,conn)
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
            upload_to_edge(file_tag, public_key, group, file_count,cipher_2,cipher_3, cuckoo_blocks, metadata, is_update, old_file_tag)
            val = '1'            
        case 'download_from_edge':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            val = download_from_edge(file_tag,public_key)
        case 'check_file_tag_exists':
            val = send_text_server(message=msg)
        case 'check_access':
            val = send_text_server(message=msg)
        case 'blocks_to_server_cuckoo':
            val = send_text_server(message=msg)
        case 'check_time_hash':
            val = send_text_server(message=msg)
        case 'check_for_update':
            val = send_text_server(message=msg)
        case 'add_user':
            val = send_text_server(message=msg)
        case 'delete_user':
            val = send_text_server(message=msg)    
        case 'large_text':
            text = get_large_text(int(arg), conn)
            l = text.split('-')
            c = l[0]
            a = l[1]
            print(f'list: {l}')
            val =check_command(c,a,text,conn)
        case 'tag':
            val = send_text_server(msg)
        case 'send_file':
            get_file(arg, conn)
            send_file_to_server(arg)
        case 'get_file':
            get_file_from_server(arg)
            send_file(arg, conn)
    if val !=1:
        return val
 
def get_large_text(count,conn):
    i=0
    large = ''
    while i<count:
        i+=1
        data = conn.recv(1024).decode(FORMAT)
        large +=data
    return large
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
    print('waiting...')
    list_string =server_socket.recv(2048).decode(FORMAT)
    print('waiting done')
    __send_to_server(DISCONNECT_MESSAGE,server_socket)
    #x =server_socket.recv(2048).decode(FORMAT)
    server_socket.close()
    print(f'msg: {message} \nreturn: {list_string}')
    if list_string:
        list = list_string.split('-')
        val = list[1]
        return val

def get_file(filename, file_conn):
    msg_length = file_conn.recv(HEADER).decode(FORMAT)
    msg_length = int(msg_length)
    msg = file_conn.recv(msg_length).decode(FORMAT)
    l = msg.split('-')
    file_size = l[1] 
    with open(filename, 'wb') as f:
        l = int(file_size)
        v = True
        while v:
            data = file_conn.recv(1024)
            f.write(data)
            l = l - len(data)
            if l<=0:
                v=False    
        '''
        data = file_conn.recv(1024)
        d_len = len(data)
        f.write(data)
        while data and d_len>1024:
            f.write(data)
            data = file_conn.recv(1024)
        #'''

def send_file(filename, file_conn):
    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            file_conn.send(data)
            data = f.read(1024)

def get_folder(count,conn):
    if not os.path.exists('files'):
        os.mkdir('files')
    #if not os.path.exists('files/blocks'):
    #    os.mkdir('files/blocks')
    if not os.path.exists(edge_input_folder_name):
        os.mkdir(edge_input_folder_name)
    print(f'count: {count}')
    for i in range(int(count)):
        print('loop: ',i)
        #msg_length = conn.recv(HEADER).decode(FORMAT)
        m = conn.recv(HEADER)
        print(f'len: {m}')
        msg_length = m.decode(FORMAT)
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        l = msg.split('-')
        file_name = l[1]
        print(f'path: {file_name}')
        get_file(file_name,conn)
        conn.send('Received File'.encode(FORMAT))
        print('loop ended')


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
    if msg_length > 1024:
        print(f'large_text1-{msg_length}')
        __send_to_server(f'large_text-{msg_length}',server_socket)
        server_socket.sendall(message)
    else:
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
    for i in range (1,int(file_count)):
        o_file_name = str(file_tag)+'_{}.bin'.format(i)
        block_name = 'block{}.bin'.format(i)
        AES.aes_encrypt_file(edge_key, iv, edge_input_folder_name, edge_output_folder_name,block_name,o_file_name)

        block_path = edge_output_folder_name+o_file_name
        mod = modulo_hash_file(block_path,prime2)
        block_tags.append(mod)
        command = 'check_block_exists'
        arg = str(mod)
        list = [command,arg]
        message = '-'.join(list)
        val = send_text_server(message)
        print(f'val: {val}')
        #val = server.check_block_exists(str(mod))
        if val=='False':
            command = 'save_block_vales'
            l = [str(mod),str(file_tag)]
            s = '+'.join(l)
            arg = s
            list = [command,arg]
            message = '-'.join(list)
            send_text_server(message)
            #server.save_block_vales(str(mod), file_tag)
            #Send only the unique ones.

    block_tags_list= '/'.join(str(b) for b in block_tags)
    #Comm: Send file to server
    command = 'upload_to_server'
    l = [str(file_tag),str(public_key), group,cipher_2,str(cipher_3),block_tags_list, cuckoo_blocks, str(metadata), is_update, str(old_file_tag)]
    s = '+'.join(l)
    arg = s
    list = [command,arg]
    message = '-'.join(list)
    print(f'upload to s: {message}')
    send_text_server(message)
    #server.upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags_list, cuckoo_blocks, metadata, is_update, old_file_tag)

def download_from_edge(file_tag, public_key):
    #Comm: Get file
    command = 'download_from_server'
    l = [str(file_tag),str(public_key)]
    s = '+'.join(l)
    arg = s
    list = [command,arg]
    message = '-'.join(list)
    val_str = send_text_server(message)
    #val = server.download_from_server(file_tag, public_key)
    if val_str == '-1':
        return '-1' # No Access
    val = val_str.split('*')
    cipher_2, cipher_3, block_tags, metadata_str = val
    metadata = metadata_str.split(',')
    _, file_count = metadata_str
    file_count = file_count[:-1]
    tag_list_string= block_tags
    tag_list = tag_list_string.split('-')
    for i in range (1,int(file_count)):
        block_name = 'block{}.bin'.format(i)
        block_tag = tag_list[i-1]
        command = 'get_file_tag_of_block'
        arg = block_tag
        list = [command,arg]
        message = '-'.join(list)
        file_tag_of_block = send_text_server(message)
        #file_tag_of_block = server.get_file_tag_of_block(block_tag) #define
        if file_tag != file_tag_of_block:
            command = 'get_index_of_block'
            l = [str(block_tag),str(file_tag)]
            s = '+'.join(l)
            arg = s
            list = [command,arg]
            message = '-'.join(list)
            index = send_text_server(message)
            #index = server.get_index_of_block(block_tag,file_tag)+1 #define
            block_suffix = file_tag_of_block
            #fetch block
        else:
            index = i
            block_suffix = file_tag
        input_file_name = str(block_suffix)+'_{}.bin'.format(index)
        #Comm: Send file to User
        AES.aes_decrypt_file(edge_key, iv, edge_down_input_folder_name, edge_output_down_folder_name,block_name,input_file_name)
    l = [cipher_2, cipher_3, metadata_str]
    l_str = '*'.join(l)    
    return l_str


start()