import os
import server
import socket 
import threading
from datetime import datetime

HEADER = 64
PORT = 5050
SERVER = socket.gethostname()
ADDR = ('', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"
edge_output_folder_name = 'files/edge_encrypt_blocks/'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)
def handle_client(conn, addr):
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
            value = check_command(command,val, conn)
            print(f'valuie: {value}')
            if value != 'dav1sh':
                conn.send(f"return-{value}".encode(FORMAT))
    conn.close()


def check_command(argument,arg, conn):
    val = 'dav1sh'
    match argument:
        case 'check_file_tag_exists':
            bool_val = server.check_file_tag_exists(file_tag=arg)
            if bool_val:
                val = 'True'
            else:
                val = 'False'
        case 'check_access':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            value = server.check_access(file_tag,public_key)
            if not value:
                val = 'False'
            else:
                val = '*'.join(str(i) for i in value)
        case 'check_block_exists':
            bool_val = server.check_block_exists(arg)
            if bool_val:
                val = 'True'
            else:
                val = 'False'
        case 'save_block_values':
            lists = arg.split('+')
            mod = lists[0]
            file_tag = lists[1]
            print(f'list: {lists}\nmod: {mod}\ntag: {file_tag}')
            server.save_block_values(mod, file_tag)
            val ='1'
        case 'get_file_tag_of_block':
            val = server.get_file_tag_of_block(block_tag=arg)
        case 'blocks_to_server_cuckoo':
            lists = arg.split('+')
            file_tag = lists[0]
            block_keys = lists[1]
            public_key = lists[2]
            val = str(server.blocks_to_server_cuckoo(file_tag,block_keys,public_key))
            #large val possibility
        case 'check_time_hash':
            lists = arg.split('+')
            file_tag =lists[0]
            public_key =lists[1]
            time_val = lists[2]
            val = str(server.check_time_hash(file_tag,public_key, time_val))
        case 'upload_to_server':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            group = lists[2]
            cipher_2 = lists[3]
            cipher_3 = lists[4]
            block_tags = lists[5]
            cuckoo_blocks = lists[6]
            metadata = lists[7]
            is_update = lists[8]
            old_file_tag = lists[9]
            server.upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, block_tags, cuckoo_blocks, metadata, is_update, old_file_tag)
            val = '1'
        case 'check_for_update':
            val = str(server.check_for_update(file_tag=arg))
        case 'add_user':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            new_public_key = lists[2]
            val = str(server.add_user(file_tag, public_key, new_public_key))
        case 'delete_user':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            new_public_key = lists[2]
            val = str(server.add_user(file_tag, public_key, new_public_key))
        case 'download_from_server':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            val = server.download_from_server(file_tag, public_key)
            #large val possibility
        case 'large_text':
            text = get_large_text(arg,conn)
            l = text.split('-')
            c = l[0]
            a = l[1]
            print(f'list: {l}')
            val =check_command(c,a,conn)

        case 'tag':
            val = get_rce(arg)
        case 'send_file':
            get_file(arg, conn)
        case 'get_file':
            send_file(arg, conn)
    return val

def get_large_text(str_len, conn):
    large = ''
    v = True
    l = int(str_len)
    while v:
        data = conn.recv(1024).decode(FORMAT)
        large +=data
        l = l-len(data)
        print(f'larfe: {large}\nDat: {data}\ntyp: {len(data)}')
        if l<=0:
            v = False
    return large

def get_rce(val):
    print(f"Here's rce value from client: {val}")
    return 'Davish'

def get_file(filename, file_conn):

    if not os.path.exists('files'):
        os.mkdir('files')
    if not os.path.exists(edge_output_folder_name):
        os.mkdir(edge_output_folder_name)
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
    # with open(filename, 'wb') as f:
    #     data = file_conn.recv(1024)
    #     while data:
    #         f.write(data)
    #         data = file_conn.recv(1024)

def send_file(filename, file_conn):
    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            file_conn.send(data)
            data = f.read(1024)


def start():
    server_socket.listen(100)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()