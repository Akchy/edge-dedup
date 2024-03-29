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
edge_output_folder_name = 'files/edge_encrypted_blocks_'
edge_down_folder_name = 'files/edge_encrypted_down_blocks_'

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
            #print(f'command: {command}, val: {val}')
            value = check_command(command,val, conn)
            #print(f'valuie: {value}')
            if value != 'dav1sh':
                conn.send(f"return-/{value}".encode(FORMAT))
    conn.close()


def check_command(argument,arg, conn):
    val = 'dav1sh'
    match argument:
        case 'folder_share':
            lists = arg.split('+')
            file_count = lists[0]
            file_tag = lists[1]
            get_folder(file_count,file_tag,conn)
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
        case 'save_block_exists_if_not_exists':
            print(f'block checking: {datetime.now()}')
            lists = arg.split('+')
            block_tags_lists = lists[0]
            file_tag = lists[1]
            value =server.save_block_exists_if_not_exists(block_tags_lists,file_tag)
            send_large_text(value,conn)
        case 'get_file_tag_of_block':
            lists = arg.split('+')
            block_tag = lists[0]
            file_tag = lists[1]
            val = server.get_file_tag_and_index_of_block(block_tag,file_tag)
        case 'blocks_to_server_cuckoo':
            lists = arg.split('+')
            file_tag = lists[0]
            block_keys = lists[1]
            public_key = lists[2]
            val = server.blocks_to_server_cuckoo(file_tag,block_keys,public_key)
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
            val = str(server.delete_user(file_tag, public_key, new_public_key))
        case 'download_from_server':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            large_text = server.download_from_server(file_tag, public_key)
            send_large_text(large_text,conn)
            #large val possibility
        case 'large_text':
            text = get_large_text(arg,conn)
            l = text.split('-')
            c = l[0]
            a = l[1]
            #print(f'list: {l}')
            val =check_command(c,a,conn)
        case 'send_file':
            lists = arg.split('+')
            file_name = lists[0]
            file_tag = lists[1]
            get_file(file_name, file_tag, conn)
        case 'get_file':
            send_file(arg, conn)
            x = conn.recv(13).decode(FORMAT)
        case 'download_folder_from_server':
            send_folder(arg,conn)
    return val

def __send(msg,conn):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    #print(f'msg: {msg}')
    conn.send(send_length)
    conn.send(message)

def get_large_text(str_len, conn):
    large = ''
    v = True
    l = int(str_len)
    while v:
        data = conn.recv(1024).decode(FORMAT)
        large +=data
        l = l-len(data)
        #print(f'larfe: {large}\nDat: {data}\ntyp: {len(data)}')
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

def get_file(filename, file_tag, file_conn):

    if not os.path.exists('files'):
        os.mkdir('files')
    edge_output_folder_name1 = edge_output_folder_name + file_tag + '/'
    if not os.path.exists(edge_output_folder_name1):
        os.mkdir(edge_output_folder_name1)
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
    f.close()
    # with open(filename, 'wb') as f:
    #     data = file_conn.recv(1024)
    #     while data:
    #         f.write(data)
    #         data = file_conn.recv(1024)

def send_file(filename, file_conn):
    with open(filename, 'rb') as f:
        data = f.read()
        msg_length = len(data)
        length_com = f'len-{msg_length}'
        l = len(length_com)
        send_length = str(l).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        file_conn.send(send_length)
        file_conn.send(length_com.encode(FORMAT))
        file_conn.sendall(data)

def send_file1(filename, file_conn):
    #Send File name
    __send(f'file_name-{filename}',file_conn)
    #Send file
    with open(filename, 'rb') as f:
        data = f.read()
        data_len = len(data)
        __send(f'len-{data_len}',file_conn)
        file_conn.sendall(data)


def get_folder(count,tag,conn):
    if not os.path.exists('files'):
        os.mkdir('files')
    edge_output_folder_name1 = edge_output_folder_name + tag + '/'
    if not os.path.exists(edge_output_folder_name1):
        os.mkdir(edge_output_folder_name1)
    #print(f'count: {count}')
    for i in range(int(count)):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        l = msg.split('-')
        file_name = l[1]
        #print(f'path: {file_name}')
        get_file(file_name,tag,conn)
        conn.send('Received File'.encode(FORMAT))


def send_folder(file_tag, conn):
    folder_name = edge_down_folder_name + str(file_tag)+'/'
    files = os.listdir(folder_name)
    for file in files:
        file_path = folder_name+file
        send_file1(file_path,conn)
        x = conn.recv(13).decode(FORMAT)

def start():
    server_socket.listen(100)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()