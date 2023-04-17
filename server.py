import hashlib
import socket
import threading
import mysql.connector
import os
import shutil
from client_thread import ClientThread

host = "0.0.0.0"
port = 8080

# Define the MySQL database connection parameters
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


def handle_upload(client_socket):
    file_name = client_socket.recv(1024).decode()
    file_size = int(client_socket.recv(1024).decode())
    file_data = client_socket.recv(file_size)

    with open(file_name, 'wb') as f:
        f.write(file_data)

    print(f"File '{file_name}' uploaded to server.")


def handle_download(client_socket):
    file_name = client_socket.recv(1024).decode()

    if not os.path.exists(file_name):
        print(f"File '{file_name}' does not exist on server.")
        return

    file_size = os.path.getsize(file_name)
    client_socket.send(str(file_size).encode())

    with open(file_name, 'rb') as f:
        file_data = f.read()

    client_socket.sendall(file_data)

    print(f"File '{file_name}' downloaded from server.")


def main():
    # Create the MySQL table if it doesn't exist
    try:
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR("
                             "255), password VARCHAR(255))")
        mysql_connection.commit()
    except mysql.connector.Error as error:
        print(f"Error creating MySQL table: {error}")
    finally:
        mysql_cursor.close()
        mysql_connection.close()

    # Create a new server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the server socket to the host and port
    server_socket.bind((host, port))

    # Start listening for incoming connections
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    while True:
        # Accept incoming connections and start a new thread for each client
        client_socket, client_address = server_socket.accept()
        client_thread = ClientThread(client_socket, client_address)
        client_thread.start()


if __name__ == '__main__':
    main()
