import hashlib
import os
import threading
import mysql

FOLDER = 'D:\\FS\\'     #"C:\\Users\\orico\\OneDrive\\שולחן העבודה\\FileSpace\\"
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
            password = data.split()[2]

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
            password = data.split()[2]

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
            file_name = FOLDER + ' '.join(data.split()[1:])
            if not os.path.exists(file_name):
                print(f"File '{file_name}' does not exist on server.")
                file_name = file_name.split('\\')[-1]
                self.client_socket.send(f"File '{file_name}' does not exist on server.".encode())
                return

            file_size = os.path.getsize(file_name)
            self.client_socket.send(str(file_size).encode())

            with open(file_name, 'rb') as f:
                file_data = f.read()

            self.client_socket.sendall(bytes(file_data))
            self.client_socket.recv(1024).decode()
            self.client_socket.send("OK".encode())

            print(f"File '{file_name}' downloaded from server.")
        elif command == "upload":
            file_name = FOLDER + ' '.join(data.split()[1:-1])

            file_size = int(data.split()[-1])
            self.client_socket.send("received".encode())
            file_data = self.client_socket.recv(file_size)

            with open(file_name, 'wb') as f:
                f.write(file_data)

            print(f"File '{file_name}' uploaded to server.")
            self.client_socket.send("OK".encode())

        # Close the MySQL connection and client socket
        mysql_cursor.close()
        mysql_connection.close()
        self.client_socket.close()
        print(f"Connection from {self.client_address} closed")

