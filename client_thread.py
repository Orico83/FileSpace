from cryptography.fernet import Fernet
import os
import shutil
import threading
from pickle import dumps, loads

import mysql
from file_classes import Directory

FOLDER = r"C:\Users\orico\Desktop\ServerFolder"
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.mysql_cursor = None
        self.mysql_connection = None
        self.serialized_dir = None
        self.username = None
        self.client_socket = client_socket
        self.client_address = client_address
        self.folder_path = None

    def run(self):
        # Verify the username and password against the MySQL table
        self.mysql_connection = mysql.connector.connect(**database_config)
        self.mysql_cursor = self.mysql_connection.cursor()
        try:
            print(f"Connection from {self.client_address}")
            # Receive the command from the client (login or signup)
            data = self.client_socket.recv(1024).decode().strip()
            command = data.split()[0]
            print(command)
            if command == "login":
                # Receive the username and password from the client
                self.username = data.split()[1]
                password = data.split()[2]
                self.serialized_dir = b''
                print(f"Username: {self.username} | Password: {password}")
                self.mysql_cursor.execute("SELECT * FROM filespace WHERE username = %s AND password = %s",
                                          (self.username, password))
                result = self.mysql_cursor.fetchone()
                if result:
                    self.client_socket.send("OK".encode())
                    # retrieve the encrypted directory from the database
                    self.serialized_dir = result[-1]

                    # check if the serialized directory object was found
                    if self.serialized_dir:
                        self.handle_commands()  # Call a method to handle subsequent commands

                else:
                    self.client_socket.send("FAIL".encode())
            elif command == "signup":
                # Receive the username and password from the client
                self.username = data.split()[1]
                password = data.split()[2]
                print(f"Username: {self.username} | Password: {password}")
                # Check if the username already exists in the table
                self.mysql_cursor.execute("SELECT * FROM filespace WHERE username = %s", (self.username,))
                result = self.mysql_cursor.fetchone()
                if result:
                    self.client_socket.send("FAIL".encode())
                else:
                    self.folder_path = os.path.join(FOLDER, self.username)
                    os.makedirs(self.folder_path, exist_ok=True)
                    self.serialized_dir = dumps(Directory(self.folder_path))
                    self.mysql_cursor.execute(
                        "INSERT INTO filespace (username, password, directory) VALUES (%s, %s, %s)",
                        (self.username, password, self.serialized_dir))
                    self.mysql_connection.commit()

                    self.client_socket.send("OK".encode())
                    self.handle_commands()  # Call a method to handle subsequent commands

            # Close the MySQL connection and client socket

        except Exception as err:
            print(err)
        finally:
            self.mysql_cursor.close()
            self.mysql_connection.close()
            self.client_socket.close()
            print(f"Connection from {self.client_address} closed")

    def handle_commands(self):
        while True:
            # Receive the command from the client
            data = self.client_socket.recv(1024).decode().strip()
            if not data:
                update_directory(self.username, self.mysql_connection)
                break  # Exit the loop if no more data is received

            # Add code to handle different commands here
            if data.startswith("download_folder"):
                self.serialized_dir = get_dir(self.username, self.mysql_connection)

                self.client_socket.send(f"size: {self.serialized_dir.__sizeof__()}".encode())
                self.client_socket.recv(1024)
                self.client_socket.send(self.serialized_dir)
            elif data.startswith("delete_item"):
                item_path = os.path.join(FOLDER, str(data.split()[1]))
                delete_item(item_path)
            elif data.startswith("rename_item"):
                item_path = os.path.join(FOLDER, data.split()[1])
                new_name = data.split()[-1]
                rename_item(item_path, new_name)
            elif data.startswith("create_file"):
                new_file_path = os.path.join(FOLDER, data.split()[1])
                if os.path.exists(new_file_path):
                    return
                # Create the new file
                with open(new_file_path, 'w'):
                    pass  # Do nothing, just create an empty file
            elif data.startswith("create_folder"):
                new_dir_path = os.path.join(FOLDER, data.split()[1])
                os.makedirs(new_dir_path)
            elif data.startswith("upload_dir"):
                self.client_socket.send("OK".encode())
                dir_size = int(data.split("||")[1])
                bytes_received = 0
                dir_data = b''
                while bytes_received < dir_size:
                    chunk = self.client_socket.recv(1024)
                    bytes_received += 1024
                    dir_data += chunk
                directory = loads(dir_data)
                location = os.path.join(FOLDER, data.split("||")[2].strip())
                print(location)
                directory.create(location)
            elif data.startswith("upload_file"):
                self.client_socket.send("OK".encode())
                dir_size = int(data.split("||")[1])
                bytes_received = 0
                file_data = b''
                while bytes_received < dir_size:
                    chunk = self.client_socket.recv(1024)
                    bytes_received += 1024
                    file_data += chunk
                file = loads(file_data)
                location = os.path.join(FOLDER, data.split("||")[2].strip())
                file.create(location)
                self.client_socket.send("OK".encode())

            else:
                self.client_socket.send("Invalid command".encode())
            update_directory(self.username, self.mysql_connection)


def delete_item(item_path):
    if os.path.isfile(item_path):
        # Delete a file
        os.remove(item_path)
    elif os.path.isdir(item_path):
        # Delete a folder and its contents
        shutil.rmtree(item_path)


def rename_item(item_path, new_name):
    try:
        new_path = os.path.join(os.path.dirname(item_path), new_name)
        os.rename(item_path, new_path)
    except Exception as err:
        print(err.args[1])


def update_directory(username, connection):
    cursor = connection.cursor()
    serialized_directory = dumps(Directory(os.path.join(FOLDER, username)))
    update_query = "UPDATE filespace SET directory = %s WHERE username = %s"
    update_values = (serialized_directory, username)
    cursor.execute(update_query, update_values)
    connection.commit()


def get_dir(username, connection):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # Retrieve the serialized directory from the database
        query = "SELECT directory FROM filespace WHERE username = %s"
        values = (username,)
        cursor.execute(query, values)
        row = cursor.fetchone()
        serialized_dir = row[0] if row else None

        return serialized_dir

    except mysql.connector.Error as error:
        print(f"Error retrieving directory from database: {error}")

