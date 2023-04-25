import socket
import mysql.connector
import os
from client_thread import ClientThread

host = "0.0.0.0"  # Host IP address where the server will be running
port = 8080  # Port number to bind the server socket

# Define the MySQL database connection parameters
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


def handle_upload(client_socket):
    """
    Handles uploading a file from the client to the server.

    Parameters:
        client_socket (socket): The socket object for the client connection.

    Returns:
        None
    """
    # Receive the file name, file size and file data from the client
    file_name = client_socket.recv(1024).decode()
    file_size = int(client_socket.recv(1024).decode())
    file_data = client_socket.recv(file_size)

    # Write the file data to disk
    with open(file_name, 'wb') as f:
        f.write(file_data)

    print(f"File '{file_name}' uploaded to server.")


def handle_download(client_socket):
    """
    Handles downloading a file from the server to the client.

    Parameters:
        client_socket (socket): The socket object for the client connection.

    Returns:
        None
    """
    # Receive the file name from the client
    file_name = client_socket.recv(1024).decode()

    # Check if the file exists on the server
    if not os.path.exists(file_name):
        print(f"File '{file_name}' does not exist on server.")
        return

    # Get the file size and send it to the client
    file_size = os.path.getsize(file_name)
    client_socket.send(str(file_size).encode())

    # Read the file data and send it to the client
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
