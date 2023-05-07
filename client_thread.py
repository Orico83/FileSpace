import hashlib
import os
import threading
import mysql
from file_classes import File, Directory

FOLDER = "C:\\Users\\orico\\OneDrive\\שולחן העבודה\\FileSpace\\"
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


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
                self.handle_commands()  # Call a method to handle subsequent commands

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
                self.handle_commands()  # Call a method to handle subsequent commands

    def handle_commands(self):
        while True:
            # Receive the command from the client
            data = self.client_socket.recv(1024).decode().strip()
            if not data:
                break  # Exit the loop if no more data is received
            command = data.split()[0]

            # Add code to handle different commands here
            if command == "command1":
                # Handle command1
                self.client_socket.send("Response to command1".encode())
            elif command == "command2":
                # Handle command2
                self.client_socket.send("Response to command2".encode())
            else:
                self.client_socket.send("Invalid command".encode())

        # Close the MySQL connection and client socket
        mysql_cursor.close()
        mysql_connection.close()
        self.client_socket.close()
        print(f"Connection from {self.client_address} closed")

