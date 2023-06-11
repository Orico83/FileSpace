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

create_users_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    password VARCHAR(255),
    friends VARCHAR(4095),
    friend_requests VARCHAR(4095)
    )
"""
create_shares_table_query = """
CREATE TABLE IF NOT EXISTS users_sharing (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sharing_user VARCHAR(255),
    shared_user VARCHAR(255),
    permission ENUM('read', 'read_write')
)
"""


def main():
    # Create the MySQL table if it doesn't exist
    mysql_connection = mysql.connector.connect(**database_config)
    mysql_cursor = mysql_connection.cursor()
    try:
        mysql_cursor.execute(create_users_table_query)
        mysql_cursor.execute(create_shares_table_query)
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
        try:
            client_socket, client_address = server_socket.accept()

            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()

        except ConnectionError as err:
            print(err)


if __name__ == '__main__':
    main()
