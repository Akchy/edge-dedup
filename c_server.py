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
            if value != 1:
                conn.send(f"return-{value}".encode(FORMAT))
    conn.close()


def check_command(argument,arg, conn):
    val = 1
    match argument:
        case 'check_file_tag_exists':
            print('hi')
            bool_val = server.check_file_tag_exists(file_tag=arg)
            print('hola')
            if bool_val:
                val = 'True'
            else:
                val = 'False'
            print(f'val: {val}')
        case 'check_access':
            lists = arg.split('+')
            file_tag = lists[0]
            public_key = lists[1]
            value = server.check_access(file_tag,public_key)
            #value = [1,2,3]
            if not value:
                val = 'False'
            else:
                val = '*'.join(str(i) for i in value)
        case 'tag':
            val = get_rce(arg)
        case 'send_file':
            get_file(arg, conn)
        case 'get_file':
            send_file(arg, conn)
    return val

def get_rce(val):
    print(f"Here's rce value from client: {val}")
    return 'Davish'

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


def start():
    server_socket.listen(100)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()