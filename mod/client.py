import socket

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
s.connect(("192.168.1.100", 1234))

# Open the file
with open("file_to_send.txt", "rb") as f:
    # Send the file
    s.sendall(f.read())

# Close the connection
s.close()
