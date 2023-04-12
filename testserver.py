import hashlib
import socket
import threading
import mysql.connector

# Define the host and port for the server
host = "0.0.0.0"
port = 8080

# Define the MySQL database connection parameters
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}

# Create the MySQL table if it doesn't exist
try:
    mysql_connection = mysql.connector.connect(**database_config)
    mysql_cursor = mysql_connection.cursor()
    mysql_cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
    mysql_connection.commit()
except mysql.connector.Error as error:
    print(f"Error creating MySQL table: {error}")
finally:
    mysql_cursor.close()
    mysql_connection.close()


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        print(f"Connection from {self.client_address}")

        # Receive the command from the client (login or signup)
        data = self.client_socket.recv(1024).decode().strip()
        command = data.split()[0]
        print(command)
        # Receive the username and password from the client
        username = data.split()[1]
        print(username)
        password = hashlib.md5(data.split()[2].encode()).hexdigest()

        print(password)

        # Verify the username and password against the MySQL table
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()
        if command == "login":
            mysql_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            result = mysql_cursor.fetchone()
            if result:
                self.client_socket.send("OK".encode())
            else:
                self.client_socket.send("FAIL".encode())
        elif command == "signup":
            # Check if the username already exists in the table
            mysql_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            result = mysql_cursor.fetchone()
            if result:
                self.client_socket.send("FAIL".encode())
            else:
                mysql_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                mysql_connection.commit()
                self.client_socket.send("OK".encode())

        # Close the MySQL connection and client socket
        mysql_cursor.close()
        mysql_connection.close()
        self.client_socket.close()
        print(f"Connection from {self.client_address} closed")

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
