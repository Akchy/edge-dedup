import socket

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to an IP address and port
s.bind(("192.168.1.100", 1234))

# Listen for incoming connections
s.listen(5)

while True:
    # Accept a connection
    c, addr = s.accept()
    print("Got connection from", addr)

    # Receive the file
    with open("received_file.txt", "wb") as f:
        while True:
            data = c.recv(1024)
            if not data:
                break
            f.write(data)

    # Close the connection
    c.close()
