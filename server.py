import os
import socket

import mysql
import mysql.connector

from client_thread import ClientThread

host = "0.0.0.0"  # Host IP address where the server will be running
port = 8080  # Port num to bind the server socket

# Define the MySQL database connection parameters
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


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
