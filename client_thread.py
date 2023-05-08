import hashlib
import os
import threading
from pickle import dumps

import mysql
from file_classes import File, Directory

FOLDER = r'C:\Users\cyber\Desktop\FS'    #"C:\\Users\\orico\\OneDrive\\שולחן העבודה\\FileSpace\\"
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.username = None
        self.client_socket = client_socket
        self.client_address = client_address
        self.folder_path = None

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
            self.username = data.split()[1]
            print(self.username)
            password = data.split()[2]

            print(password)
            mysql_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (self.username, password))
            result = mysql_cursor.fetchone()
            if result:
                self.client_socket.send("OK".encode())
                self.folder_path = os.path.join(FOLDER, self.username)
                self.handle_commands()  # Call a method to handle subsequent commands

            else:
                self.client_socket.send("FAIL".encode())
        elif command == "signup":
            # Receive the username and password from the client
            self.username = data.split()[1]
            print(self.username)
            password = data.split()[2
            ]

            print(password)
            # Check if the username already exists in the table
            mysql_cursor.execute("SELECT * FROM users WHERE username = %s", (self.username,))
            result = mysql_cursor.fetchone()
            if result:
                self.client_socket.send("FAIL".encode())
            else:
                mysql_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (self.username, password))
                mysql_connection.commit()
                self.folder_path = os.path.join(FOLDER, self.username)
                os.makedirs(self.folder_path)
                self.client_socket.send("OK".encode())
                self.handle_commands()  # Call a method to handle subsequent commands

    # Close the MySQL connection and client socket
        mysql_cursor.close()
        mysql_connection.close()
        self.client_socket.close()
        print(f"Connection from {self.client_address} closed")

    def handle_commands(self):
        while True:
            # Receive the command from the client
            data = self.client_socket.recv(1024).decode().strip()
            if not data:
                break  # Exit the loop if no more data is received

            # Add code to handle different commands here
            if data.startswith("download_folder"):
                folder = Directory(self.folder_path)
                # Handle command1
                self.client_socket.send(dumps(folder))
            elif data.startswith("command2"):
                # Handle command2
                self.client_socket.send("Response to command2".encode())
            else:
                self.client_socket.send("Invalid command".encode())



