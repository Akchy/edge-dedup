import socket 
import threading
from datetime import datetime

HEADER = 64
PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-Out"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
#lock = threading.Lock()
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            #lock.acquire()
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            str_to_list = msg.split('-')
            now = datetime.now()

            #current_time = now.strftime("%H:%M:%S")
            print(f'{now}:  {str_to_list[1]}')
            #command = str_to_list[0]
            #val = str_to_list[1]
            #check_command(command,val)
            #print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))
            #lock.release()
    print('done')
    conn.close()


def check_command(argument,val):
    match argument:
        case 'rce':
            get_rce(val)
        case 'file_tag':
            get_file_tag(val)
        case 2:
            return "two"
        case default:
            return "something"
 

def get_rce(val):
    print(f"Here's rce value from client: {val}")


def get_file_tag(val):
    print(f"Here's file_tag value from client: {val}")

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()