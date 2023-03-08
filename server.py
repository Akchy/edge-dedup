import socket 
import threading
from datetime import datetime

HEADER = 64
PORT = 5050
SERVER = socket.gethostname()
ADDR = ('', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
def handle_client(conn, addr):
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
        check_command(command,val, conn)
        #conn.send("Msg received".encode(FORMAT))
    conn.close()


def check_command(argument,val, conn):
    match argument:
        case 'tag':
            get_rce(val)
        case 'send_file':
            get_file(val, conn)
        case 'get_file':
            send_file(val, conn)

def get_rce(val):
    print(f"Here's rce value from client: {val}")

def get_file(filename, file_conn):
    '''
    file_socket = socket.socket()

    # bind file socket to localhost and port 8001
    file_socket.bind(('', 5051))

    # listen for incoming connections on file socket
    file_socket.listen()

    # accept incoming file transfer connection
    file_conn, file_addr = file_socket.accept()

    #'''
    # receive file contents from client and save to disk
    with open(filename, 'wb') as f:
        data = file_conn.recv(1024)
        while data:
            f.write(data)
            data = file_conn.recv(1024)

    # close file transfer connection and socket
    #file_conn.close()
    #file_socket.close()

def send_file(filename, file_conn):
    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            file_conn.send(data)
            data = f.read(1024)


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()