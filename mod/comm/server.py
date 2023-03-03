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
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            str_to_list = msg.split('-')
            now = datetime.now()
            command = str_to_list[0]
            val = str_to_list[1]
            check_command(command,val)
            conn.send("Msg received".encode(FORMAT))
    conn.close()


def check_command(argument,val):
    match argument:
        case 'tag':
            get_rce(val)
 

def get_rce(val):
    print(f"Here's rce value from client: {val}")

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()