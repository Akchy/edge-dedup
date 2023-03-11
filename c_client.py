import socket
from datetime import datetime

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"
EDGE = "10.0.0.2"
ADDR = (EDGE, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def __send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    #return val


def send_text(key, str):
    list = [key,str]
    l_str = '-'.join(list)
    __send(l_str)
    val=client.recv(1024).decode(FORMAT)
    print(f'{val}')
    
def send_file(filename):
    send_file_name_list = ['send_file', filename]
    send_file_name_string = '-'.join(send_file_name_list)
    __send(send_file_name_string)

    with open(filename, 'rb') as f:
        data = f.read(1024)
        while data:
            client.send(data)
            data = f.read(1024)
 
def get_file(filename):
    get_file_name_list = ['get_file', filename]
    get_file_name_string = '-'.join(get_file_name_list)
    __send(get_file_name_string)

    # receive file contents from server and save to disk
    with open(filename, 'wb') as f:
        data = client.recv(1024)
        while data:
            f.write(data)
            data = client.recv(1024)

#send_text('tag','hello there user with Public Key')

send_file('cc.txt')

#get_file('ss.txt')
client.close()