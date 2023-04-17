import hashlib
import os
import threading

import mysql

FOLDER = "C:\\Users\\orico\\OneDrive\\שולחן העבודה\\FileSpace\\"
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


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.filename = None

    def run(self):
        print(f"Connection from {self.client_address}")

        # Receive the command from the client (login or signup)
        data = self.client_socket.recv(1024).decode().strip()
        command = data.split()[0]
        print(command)

        # Verify the username and password against the MySQL table
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()
        if command == "login":
            # Receive the username and password from the client
            username = data.split()[1]
            print(username)
            password = hashlib.md5(data.split()[2].encode()).hexdigest()

            print(password)
            mysql_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            result = mysql_cursor.fetchone()
            if result:
                self.client_socket.send("OK".encode())
            else:
                self.client_socket.send("FAIL".encode())
        elif command == "signup":
            # Receive the username and password from the client
            username = data.split()[1]
            print(username)
            password = hashlib.md5(data.split()[2].encode()).hexdigest()

            print(password)
            # Check if the username already exists in the table
            mysql_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            result = mysql_cursor.fetchone()
            if result:
                self.client_socket.send("FAIL".encode())
            else:
                mysql_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                mysql_connection.commit()
                self.client_socket.send("OK".encode())
        elif command == "download":
            file_name = FOLDER + data.split()[1]
            if not os.path.exists(file_name):
                print(f"File '{file_name}' does not exist on server.")
                return

            file_size = os.path.getsize(file_name)
            self.client_socket.send(str(file_size).encode())

            with open(file_name, 'rb') as f:
                file_data = f.read()

            self.client_socket.sendall(bytes(file_data))

            print(f"File '{file_name}' downloaded from server.")

        # Close the MySQL connection and client socket
        mysql_cursor.close()
        mysql_connection.close()
        self.client_socket.close()
        print(f"Connection from {self.client_address} closed")

    def upload(self):
        file_name = self.filename.get()
        if not os.path.exists(file_name):
            print(f"File '{file_name}' does not exist.")
            return

        file_size = os.path.getsize(file_name)
        self.send_command(f"upload {file_name} {file_size}")

        with open(file_name, 'rb') as f:
            file_data = f.read()

        self.socket.sendall(file_data)

        print(f"File '{file_name}' uploaded to server.")

    def download(self):
        file_name = self.filename.get()
        self.send_command(f"download {file_name}")

        file_size = int(self.socket.recv(1024).decode())
        file_data = self.socket.recv(file_size)

        with open(file_name, 'wb') as f:
            f.write(file_data)

        print(f"File '{file_name}' downloaded from server.")

    def handle_command(self, command):
        parts = command.split()
        if parts[0] == "exit":
            self.running = False
        elif parts[0] == "upload":
            self.upload()
        elif parts[0] == "download":
            self.download()
        else:
            self.socket.sendall(command.encode())
            response = self.socket.recv(1024).decode()
            print(response)
