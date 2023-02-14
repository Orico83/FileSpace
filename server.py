import socket
from pickle import loads

SERVER_IP = '0.0.0.0'
PORT = 8080
QUEUE_LEN = 10
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, PORT))
server_socket.listen()

print(f"server listening on {SERVER_IP}: {PORT}")

while True:
    client_socket, addr = server_socket.accept()
    print(f"connected by {addr}")
    user = client_socket.recv(1024)
    username = user[0]
    password = user[1]
    print(f"Creating user {username}")
    # add to database

    message = f"User {username} created"
    client_socket.send(message.encode())
    client_socket.close()
