import os
import socket
import threading
import time

import mysql
import mysql.connector
from cryptography.fernet import Fernet

from client_thread import ClientThread

KEY = b'60MYIZvk0DXCJJWEDVf3oFD4zriwOvDrYkJGgQETf5c='

fernet = Fernet(KEY)
host = "0.0.0.0"  # Host IP address where the server will be running
port = 8080  # Port num to bind the server socket

# Define the MySQL database connection parameters
database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}

# Define the SQL statement to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    password VARCHAR(255),
    friends VARCHAR(1000),
    friend_requests VARCHAR(1000)
    )
"""



class UpdateUsersThread(threading.Thread):
    def __init__(self, clients, db_config):
        super().__init__()
        self.clients = clients
        self.database_config = db_config
        self.stop_event = threading.Event()
        self.last_user_list = []

    def run(self):
        # Continuously check for changes in the users database
        while not self.stop_event.is_set():
            # Perform your database query to get the updated user list
            updated_users = self.get_updated_users_from_database()

            # Update the user list for all connected clients
            for client in self.clients:
                self.send_updated_users_to_client(client, updated_users)

            # Sleep for a certain interval before checking for updates again
            time.sleep(5)

    def stop(self):
        # Set the stop event to exit the thread
        self.stop_event.set()

    def get_updated_users_from_database(self):
        # Perform the necessary query to fetch the updated user list from the database
        # Return the updated user list
        updated_users = []
        # Establish a connection to the database
        connection = mysql.connector.connect(**self.database_config)
        cursor = connection.cursor()
        try:
            # Execute the query to fetch the updated user list
            cursor.execute("SELECT username FROM users")

            # Fetch all the usernames from the result
            rows = cursor.fetchall()
            updated_users = [row[0] for row in rows]

        except mysql.connector.Error as error:
            print("Error fetching updated user list:", error)
        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()

        return updated_users

    def send_updated_users_to_client(self, client, updated_users):
        try:
            # Convert the updated users list to a string
            user_list = ",".join(updated_users)

            # Check if the user list has changed
            if user_list != self.last_user_list:
                # Encrypt and send the updated user list to the client
                encrypted_data = fernet.encrypt(user_list.encode())
                client.client_socket.send(encrypted_data)

                self.last_user_list = user_list

        except Exception as e:
            print("Error sending updated user list to client:", e)


def main():
    # Create the MySQL table if it doesn't exist
    clients = []
    try:
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute(create_table_query)
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
    """# Create an instance of UpdateUsersThread and start the thread
    update_thread = UpdateUsersThread(clients, database_config)
    update_thread.start()"""

    while True:
        # Accept incoming connections and start a new thread for each client
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()
            clients.append(client_thread)

        except Exception as err:
            print(err)
            clients.remove(client_thread)


if __name__ == '__main__':
    main()
