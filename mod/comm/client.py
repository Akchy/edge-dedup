import socket
from datetime import datetime

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-Out"
SERVER = "10.0.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    val =client.recv(2048).decode(FORMAT)
    now = datetime.now()

    #current_time = now.strftime("%H:%M:%S")
    print(f'{now}: {val}')
    return val

key_list = ['key','hello there user with Public Key']
key_string = '-'.join(key_list)
#file_tag_list = ['tag','12345346']
file_tag_list = ['tag']
val = send(key_string)
file_tag_list.append(val)
file_tag_string = '-'.join(file_tag_list)
send(file_tag_string)

send(DISCONNECT_MESSAGE)