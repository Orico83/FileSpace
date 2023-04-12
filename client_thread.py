from threading import Thread

import mysql.connector as mysql


class ClientThread(Thread):
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
        password = data.split()[2]
        print(password)

        # Verify the username and password against the MySQL table
        mysql_connection = mysql.connect(host="localhost",
                                         user="root",
                                         passwd="OC8305",
                                         database="test")
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
