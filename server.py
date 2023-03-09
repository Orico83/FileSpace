import socket
import traceback
from pickle import loads
from users_database import UsersDatabase
from threading import Thread

SERVER_IP = '0.0.0.0'
PORT = 8080
QUEUE_LEN = 10


print(f"server listening on {SERVER_IP}: {PORT}")


def handle_client(client_socket, addr):
    try:
        print(f"connected by {addr}")
        while True:
            data = loads(client_socket.recv(1024))
            print(data)
            if not data:
                break
    except ConnectionResetError as err:
        print(err)
    finally:
        print(f"Connection closed by {addr}")
        client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()
        thread = Thread(target=handle_client, args=(client_socket, addr))
        thread.start()


if __name__ == '__main__':
    main()
