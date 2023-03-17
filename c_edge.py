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


edge_input_folder_name = 'files/encrypted_blocks_'
edge_output_folder_name = 'files/edge_encrypted_blocks_'
edge_down_input_folder_name = 'files/edge_encrypted_blocks_'
edge_output_down_folder_name = 'files/edge_decrypted_blocks_'


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
            #print(f'command: {command}, val: {val}')        
            value = check_command(command,val,msg,conn)
            if value != 'dav1sh':
                conn.send(f"return-/{value}".encode(FORMAT))
    conn.close()


def check_command(key,arg,msg,conn):
    val = 'dav1sh'
    match key:
        case 'folder_share':
            lists = arg.split('+')
            file_count = lists[0]
            file_tag = lists[1]
            get_folder(file_count,file_tag,conn)
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
            large_text = download_from_edge(file_tag,public_key)
            send_large_text(large_text,conn)
        case 'download_folder_from_edge':
            send_folder_to_user(arg, conn)
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
            #print(f'list: {l}')
            val =check_command(c,a,text,conn)
        # case 'tag':
        #     val = send_text_server(msg)
        # # case 'send_file':
        # #     get_file(arg, conn)
        # #     send_file_to_server(arg)
        # case 'get_file':
        #     get_file_from_server(arg)
        #     send_file(arg, conn)
    if val !=1:
        return val
 
def get_large_text(str_len,conn):
    large = ''
    v = True
    l = int(str_len)
    while v:
        data = conn.recv(1024).decode(FORMAT)
        large +=data
        l = l-len(data)
        if l<=0:
            v = False
    return large

def send_large_text(text,conn):
    #send length
    message = text.encode(FORMAT)
    #print(f'Large_txt: {message}')
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    #sendall
    conn.sendall(message)

def send_text_server(message,large='N'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDR)
    __send_to_server(message,server_socket)
    if large=='N':
        list_string =server_socket.recv(2048).decode(FORMAT)
    else:
        msg_len_str = server_socket.recv(HEADER).decode(FORMAT)
        msg_len = int(msg_len_str)
        list_string = get_large_text(msg_len,server_socket)
    __send_to_server(DISCONNECT_MESSAGE,server_socket)
    #x =server_socket.recv(2048).decode(FORMAT)
    server_socket.close()
    #print(f'msg: {message} \nreturn: {list_string}')
    if large=='Y':
        return list_string
    elif list_string:
        list = list_string.split('-/')
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

def __send(msg,conn):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    #print(f'msg: {msg}')
    conn.send(send_length)
    conn.send(message)

def send_file(filename, file_conn):
    #Send File name
    __send(f'file_name-{filename}',file_conn)
    #Send file
    with open(filename, 'rb') as f:
        data = f.read()
        data_len = len(data)
        __send(f'len-{data_len}',file_conn)
        #file_conn.send(f'file_name-{filename}-{data_len}'.encode(FORMAT))
        file_conn.sendall(data)

def get_folder(count,tag,conn):
    if not os.path.exists('files'):
        os.mkdir('files')
    edge_input_folder_name1 = edge_input_folder_name + str(tag)+'/'
    if not os.path.exists(edge_input_folder_name1):
        os.mkdir(edge_input_folder_name1)
    #print(f'count: {count}')
    for i in range(int(count)):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        l = msg.split('-')
        file_name = l[1]
        #print(f'path: {file_name}')
        get_file(file_name,conn)
        conn.send('Received File'.encode(FORMAT))

def send_folder_to_user(file_tag, conn):
    folder_name = edge_output_down_folder_name + str(file_tag)+'/'
    files = os.listdir(folder_name)
    for file in files:
        file_path = folder_name+file
        send_file(file_path,conn)
        x = conn.recv(13).decode(FORMAT)

def send_file_to_server(filename,file_tag):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDR)
    li = [filename,file_tag]
    args = '+'.join(li)
    send_file_name_list = ['send_file',args]
    send_file_name_string = '-'.join(send_file_name_list)
    __send_to_server(send_file_name_string,server_socket)

    with open(filename, 'rb') as f:
        data = f.read()
        __send_to_server(f'len-{len(data)}',server_socket)
        server_socket.sendall(data)
        # data = f.read(1024)
        # while data:
        #     server_socket.send(data)
        #     data = f.read(1024)
    server_socket.close()

def get_file_from_server(filename):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(SERVER_ADDR)
    get_file_name_list = ['get_file', filename]
    get_file_name_string = '-'.join(get_file_name_list)
    __send_to_server(get_file_name_string,server_socket)
    msg_length = server_socket.recv(HEADER).decode(FORMAT)
    msg_length = int(msg_length)
    msg = server_socket.recv(msg_length).decode(FORMAT)
    l = msg.split('-')
    file_size = l[1] 
    with open(filename, 'wb') as f:
        l = int(file_size)
        v = True
        while v:
            data = server_socket.recv(1024)
            f.write(data)
            l = l - len(data)
            if l<=0:
                v=False 
    server_socket.send('Received File'.encode(FORMAT))
    server_socket.close()

def __send_to_server(msg,server_socket):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    if msg_length > 1024:
        #print(f'large_text1-{msg_length}')
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
        block_name = 'block{}.bin'.format(i)
        edge_output_folder_name1 = edge_output_folder_name + str(file_tag)+'/'
        edge_input_folder_name1 = edge_input_folder_name + str(file_tag)+'/'
        AES.aes_encrypt_file(edge_key, iv, edge_input_folder_name1, edge_output_folder_name1,block_name)
        block_path = edge_output_folder_name1+block_name
        mod = modulo_hash_file(block_path,prime2)
        block_tags.append(mod)
        command = 'check_block_exists'
        arg = str(mod)
        list = [command,arg]
        message = '-'.join(list)
        val = send_text_server(message)
        #val = server.check_block_exists(str(mod))
        if val=='False':
            command = 'save_block_values'
            l = [str(mod),str(file_tag)]
            s = '+'.join(l)
            arg = s
            list = [command,arg]
            message = '-'.join(list)
            send_text_server(message)
            send_file_to_server(block_path,file_tag)
            #Send only the unique ones.

    block_tags_list= '/'.join(str(b) for b in block_tags)
    command = 'upload_to_server'
    l = [str(file_tag),str(public_key), group,cipher_2,str(cipher_3),block_tags_list, cuckoo_blocks, str(metadata), is_update, str(old_file_tag)]
    s = '+'.join(l)
    arg = s
    list = [command,arg]
    message = '-'.join(list)
    #print(f'upload to s: {message}')
    send_text_server(message)
    #server.upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags_list, cuckoo_blocks, metadata, is_update, old_file_tag)

def download_from_edge(file_tag, public_key):
    command = 'download_from_server'
    l = [str(file_tag),str(public_key)]
    s = '+'.join(l)
    arg = s
    list = [command,arg]
    message = '-'.join(list)
    val_str = send_text_server(message,large='Y')
    #val = server.download_from_server(file_tag, public_key)
    if val_str == '-1':
        return '-1' # No Access
    val = val_str.split('*')
    cipher_2 = val[0]
    cipher_3 = val[1]
    block_tags = val[2]
    metadata_str  = val[3]
    metadata = metadata_str.split(',')
    _, file_count = metadata
    file_count = file_count[:-1]
    tag_list_string= block_tags
    tag_list = tag_list_string.split('/')
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
        if not os.path.exists('files'):
            os.mkdir('files')
        edge_down_input_folder_name1 = edge_down_input_folder_name + str(block_suffix)+'/'
        if not os.path.exists(edge_down_input_folder_name1):
            os.mkdir(edge_down_input_folder_name1)
        file_path = edge_down_input_folder_name1+block_name
        get_file_from_server(file_path)
        edge_output_down_folder_name1 = edge_output_down_folder_name + str(file_tag)+'/'
        AES.aes_decrypt_file(edge_key, iv, edge_down_input_folder_name1, edge_output_down_folder_name1,block_name)
    l = [cipher_2, cipher_3, metadata_str]
    l_str = '*'.join(l)    
    return l_str


start()