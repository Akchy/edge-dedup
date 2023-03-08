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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(SERVER_ADDR)
#lock = threading.Lock()
def handle_user(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
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
            check_command(command,val,msg)
            conn.send("Msg received".encode(FORMAT))
    conn.close()


def check_command(argument,val,msg):
    match argument:
        case 'key':
            print(f'val: {val}')
        case 'tag':
            send_to_server(msg)
            send_to_server(DISCONNECT_MESSAGE)
        case default:
            print("something")
 


def send_to_server(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server.send(send_length)
    server.send(message)
    val =server.recv(2048).decode(FORMAT)
    return val

def start():
    edge.listen()
    print(f"[LISTENING] Edge is listening on {EDGE}")
    while True:
        conn, addr = edge.accept()
        thread = threading.Thread(target=handle_user, args=(conn, addr))
        thread.start()

start()