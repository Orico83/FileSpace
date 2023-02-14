import socket
from pickle import dumps

SERVER_IP = '127.0.0.1'
PORT = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

username = input("Enter a username: ")
password = input("Create password: ")
client_socket.send(dumps([username, password]))


message = client_socket.recv(1024).decode()
print(message)
