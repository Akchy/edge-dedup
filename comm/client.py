import socket
from datetime import datetime

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"
SERVER = "10.0.0.2"
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
    #val =client.recv(2048).decode(FORMAT)
    
    #current_time = now.strftime("%H:%M:%S")
    #print(f'{val}')
    #return val


def send_text(key, str):
    list = [key,str]
    l_str = '-'.join(list)
    send(l_str)
    
def send_file(filename):
    send_file_name_list = ['send_file', filename]
    send_file_name_string = '-'.join(send_file_name_list)
    send(send_file_name_string)

    #file_socket = socket.socket()

    # connect to server on file transfer port 8001
    #file_socket.connect((SERVER, 5051))

    # send file contents to server
    with open('cc.txt', 'rb') as f:
        data = f.read(1024)
        while data:
            client.send(data)
            data = f.read(1024)

    # close file transfer socket
    #file_socket.close()
 
def get_file(filename):
    get_file_name_list = ['get_file', filename]
    get_file_name_string = '-'.join(get_file_name_list)
    send(get_file_name_string)

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