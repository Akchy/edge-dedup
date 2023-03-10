import os
import socket 
import threading
from datetime import datetime

HEADER = 64
PORT = 5050
EDGE = socket.gethostname()
EDGE_ADDR = ('', PORT)
SERVER_ADDR = ('10.0.0.3', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"

edge = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
edge.bind(EDGE_ADDR)

#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.connect(SERVER_ADDR)
#lock = threading.Lock()
def handle_user(conn, addr):
    connected = True
    #while connected:
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        str_to_list = msg.split('-')
        command = str_to_list[0]
        val = str_to_list[1]
        value = check_command(command,val,msg,conn)
        conn.send(f"return-{value}".encode(FORMAT))
    conn.close()


def check_command(argument,arg,msg,conn):
    val = 1
    match argument:
        case 'key':
            print(f'val: {arg}')
        case 'tag':
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect(SERVER_ADDR)
            __send_to_server(msg)
            __send_to_server(DISCONNECT_MESSAGE)
            val =server.recv(2048).decode(FORMAT)
        case 'send_file':
            get_file(arg, conn)
            send_file_to_server('ss.txt')
        case 'get_file':
            send_file(arg, conn)
        case default:
            print("something")
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

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(SERVER_ADDR)
    send_file_name_list = ['send_file',filename]
    send_file_name_string = '-'.join(send_file_name_list)
    x =__send_to_server(send_file_name_string,server)

    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            server.send(data)
            data = f.read(1024)
    server.close()


def __send_to_server(msg,server_socket):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server_socket.send(send_length)
    server_socket.send(message)

def start():
    edge.listen()
    print(f"[LISTENING] Edge is listening on {EDGE}")
    while True:
        conn, addr = edge.accept()
        thread = threading.Thread(target=handle_user, args=(conn, addr))
        thread.start()

start()