import pathlib
from cryptography.fernet import Fernet, InvalidToken
import rsa
import os
import shutil
import threading
from pickle import dumps, loads
import mysql
from file_classes import Directory

FOLDER = "./ServerFolder"
CHUNK_SIZE = 4096
HEADER_SIZE = 10
public_key, private_key = rsa.newkeys(1024)
SYMMETRIC_KEY = Fernet.generate_key()
fernet = Fernet(SYMMETRIC_KEY)
waiting_commands = {}
connected_users = []

database_config = {
    "host": "localhost",
    "user": "root",
    "password": "OC8305",
    "database": "test"
}


def send_data(sock, msg, send_bytes=False):
    """
    Sends data over a socket connection.

    :param sock: The socket object representing the connection.
    :param msg: The message to be sent.
    :param send_bytes: A boolean flag indicating whether the message is already bytes (default is False).
    :returns: None
    """
    if not send_bytes:
        msg = msg.encode()
    msg = fernet.encrypt(msg)
    msg_len = str(len(msg)).encode()
    sock.send(fernet.encrypt(msg_len))  # Exactly 100 bytes
    sock.send(msg)


def receive_data(sock, return_bytes=False):
    """
    Receives data over a socket connection.

    :param sock: The socket object representing the connection.
    :param return_bytes: A boolean flag indicating whether the received data should be returned as bytes
    (default is False).
    :returns: The received data.
    """
    try:
        data = b''
        bytes_received = 0
        msg_len = int(fernet.decrypt(sock.recv(100)).decode())
        while bytes_received < msg_len:
            chunk = sock.recv(CHUNK_SIZE)
            bytes_received += len(chunk)
            data += chunk
        data = fernet.decrypt(data)
        if not return_bytes:
            data = data.decode()
        return data
    except ConnectionResetError as err:
        print(err)
        sock.close()


class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.mysql_connection = None
        self.username = None
        self.client_socket = client_socket
        self.client_address = client_address
        self.folder_path = None
        self.friends = []
        self.friend_requests = []
        self.username_lock = None  # Lock for the username
        self.lock = threading.Lock()

    def run(self):
        mysql_cursor = None
        mysql_connection = None
        print(f"Connection from {self.client_address}")
        self.client_socket.send(public_key.save_pkcs1("PEM"))
        public_partner = rsa.PublicKey.load_pkcs1(self.client_socket.recv(1024))
        # Encrypt the symmetric key using the client's public key
        encrypted_symmetric_key = rsa.encrypt(SYMMETRIC_KEY, public_partner)
        # Send the encrypted symmetric key to the client
        self.client_socket.send(encrypted_symmetric_key)
        try:
            while True:
                # Receive the command from the client (login or signup)
                try:
                    data = receive_data(self.client_socket)
                except (OSError, InvalidToken) as err:
                    print(err)
                    print(f"Connection from {self.client_address} closed")
                    break
                command = data.split()[0]
                print(command)

                # Verify the username and password against the MySQL table
                mysql_connection = mysql.connector.connect(**database_config)
                mysql_cursor = mysql_connection.cursor()
                if command == "login":
                    # Receive the username and password from the client
                    self.username = data.split()[1]
                    password = data.split()[2]
                    print(f"Username: {self.username} | Password: {password}")

                    mysql_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                                         (self.username, password))
                    result = mysql_cursor.fetchone()
                    if result:
                        if self.username in connected_users:
                            send_data(self.client_socket, "User already connected")
                        else:
                            waiting_commands[self.username] = []
                            connected_users.append(self.username)
                            send_data(self.client_socket, "OK")
                            self.folder_path = os.path.join(FOLDER, self.username)
                            self.friends = [] if result[3] is None else result[3].split(',')
                            self.friend_requests = [] if result[4] is None else result[4].split(',')
                            self.handle_commands(mysql_connection,
                                                 mysql_cursor)  # Call a method to handle subsequent commands

                    else:
                        send_data(self.client_socket, "FAIL")
                elif command == "signup":
                    # Receive the username and password from the client
                    self.username = data.split()[1]
                    password = data.split()[2]
                    print(f"Username: {self.username} | Password: {password}")
                    # Check if the username already exists in the table
                    mysql_cursor.execute("SELECT * FROM users WHERE username = %s", (self.username,))
                    result = mysql_cursor.fetchone()
                    if result:
                        send_data(self.client_socket, "FAIL")
                    else:
                        connected_users.append(self.username)
                        mysql_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                                             (self.username, password))
                        mysql_connection.commit()
                        self.folder_path = os.path.join(FOLDER, self.username)
                        os.makedirs(self.folder_path)
                        send_data(self.client_socket, "OK")
                        self.handle_commands(mysql_connection,
                                             mysql_cursor)  # Call a method to handle subsequent commands
        except InvalidToken:
            # Close the MySQL connection and client socket
            if mysql_cursor is not None:
                mysql_cursor.close()
            if mysql_connection is not None:
                mysql_connection.close()
            self.client_socket.close()

            connected_users.remove(self.username)
            print(f"Connection from {self.client_address} closed")

    def handle_commands(self, mysql_connection, mysql_cursor):
        while True:
            # Receive the command from the client
            try:
                data = receive_data(self.client_socket)
            except (InvalidToken, ConnectionError):
                self.client_socket.close()
                connected_users.remove(self.username)
                print(f"Connection from {self.client_address} closed")
                break

            if not data:
                break  # Exit the loop if no more data is received

            if data.startswith("download_folder"):
                try:
                    folder = Directory(self.folder_path)
                except FileNotFoundError:
                    os.makedirs(self.folder_path)
                    folder = Directory(self.folder_path)
                serialized_dir = dumps(folder)
                send_data(self.client_socket, serialized_dir, send_bytes=True)
                print(f"Sent {folder.path} to {self.username}")
            elif data.startswith("get_shared_folders"):
                send_data(self.client_socket, str(len(get_users_user_is_sharing_with(self.username))))
                for user in get_users_sharing_with_user(self.username):
                    print(f"sending {user} to {self.username}")
                    folder = Directory(os.path.join(FOLDER, user))
                    serialized_dir = dumps(folder)
                    send_data(self.client_socket, serialized_dir, send_bytes=True)
            elif data.startswith("delete_item"):
                rel_path = data.split("||")[1].strip()
                item_path = os.path.join(FOLDER, rel_path)
                with self.lock:
                    delete_item(item_path)
                print(f"Deleted {item_path}")
                modified_folder = pathlib.Path(rel_path).parts[0]
                update_command(data, self.username, modified_folder)
            elif data.startswith("rename_item"):
                rel_path = data.split("||")[1].strip()
                item_path = os.path.join(FOLDER, rel_path)
                new_name = data.split("||")[-1].strip()
                with self.lock:
                    rename_item(item_path, new_name)
                print(f"Renamed {item_path} to {new_name}")
                modified_folder = pathlib.Path(rel_path).parts[0]
                update_command(data, self.username, modified_folder)
            elif data.startswith("create_file"):
                rel_path = data.split("||")[1].strip()
                new_file_path = os.path.join(FOLDER, rel_path)
                if os.path.exists(new_file_path):
                    return
                with self.lock:
                    # Create the new file
                    with open(new_file_path, 'w'):
                        pass  # Do nothing, just create an empty file
                print(f"File {new_file_path} created")
                modified_folder = pathlib.Path(rel_path).parts[0]
                update_command(data, self.username, modified_folder)
            elif data.startswith("create_folder"):
                rel_path = data.split("||")[1].strip()
                new_dir_path = os.path.join(FOLDER, rel_path)
                os.makedirs(new_dir_path, exist_ok=True)
                print(f"Folder {new_dir_path} created")
                modified_folder = pathlib.Path(rel_path).parts[0]
                update_command(data, self.username, modified_folder)
            elif data.startswith("upload_dir"):
                serialized_dir = receive_data(self.client_socket, return_bytes=True)
                directory = loads(serialized_dir)
                rel_path = data.split("||")[1].strip()  # Extract the relative path
                location = os.path.join(FOLDER, rel_path)  # Create the target location
                with self.lock:
                    directory.create(location)  # Create the directory at the target location
                print(f"Folder {location} uploaded")
                modified_folder = pathlib.Path(rel_path).parts[0]  # Get the modified folder name from the relative path
                update_command((data, serialized_dir), self.username, modified_folder)  # Add the command to waiting_commands
            elif data.startswith("upload_file"):
                serialized_file = receive_data(self.client_socket, return_bytes=True)
                file = loads(serialized_file)
                rel_path = data.split("||")[1].strip()
                file_path = os.path.join(FOLDER, rel_path)
                with self.lock:
                    file.create(file_path)
                print(f"File {file_path} uploaded")
                modified_folder = pathlib.Path(rel_path).parts[0]
                update_command((data, serialized_file), self.username, modified_folder)
            elif data.startswith("copy"):
                rel_copied_item_path = data.split("||")[1]
                rel_destination_path = data.split("||")[2]
                copied_item_path = os.path.join(FOLDER, rel_copied_item_path)
                destination_path = os.path.join(FOLDER, rel_destination_path)
                with self.lock:
                    # Copy the file or folder
                    if os.path.isfile(copied_item_path):
                        try:
                            # Copy a file
                            shutil.copy2(copied_item_path, destination_path)
                            print(f"Copied file {copied_item_path} to {destination_path}")
                        except shutil.SameFileError:
                            pass
                    elif os.path.isdir(copied_item_path):
                        try:
                            # Copy a folder
                            shutil.copytree(copied_item_path,
                                            os.path.join(destination_path, os.path.basename(copied_item_path)))
                            print(f"Copied folder {copied_item_path} to {destination_path}")
                        except FileExistsError:
                            pass
                modified_folder = pathlib.Path(rel_copied_item_path).parts[0]
                update_command(data, self.username, modified_folder)
            elif data.startswith("move"):
                rel_cut_item_path = data.split("||")[1]
                rel_destination_path = data.split("||")[2]
                cut_item_path = os.path.join(FOLDER, rel_cut_item_path)
                destination_path = os.path.join(FOLDER, rel_destination_path)
                with self.lock:
                    try:
                        # Move the file or folder
                        shutil.move(cut_item_path, destination_path)
                        print(f"Moved {cut_item_path} to {destination_path}")
                    except shutil.Error:
                        pass
                modified_folder = pathlib.Path(rel_cut_item_path).parts[0]
                update_command(data, self.username, modified_folder)
            elif data.startswith("file_edit"):
                rel_path = data.split("||")[1]
                file_path = os.path.join(FOLDER, rel_path)
                file_data = receive_data(self.client_socket, return_bytes=True)
                # Acquire the lock before opening the file and writing to it
                with self.lock:
                    with open(file_path, "wb") as f:
                        f.write(file_data)
                modified_folder = pathlib.Path(rel_path).parts[0]
                update_command((data, file_data), self.username, modified_folder)
            elif data.startswith("refresh"):
                with self.lock:
                    try:
                        print(waiting_commands)
                        mysql_connection = mysql.connector.connect(**database_config)
                        mysql_cursor = mysql_connection.cursor()
                        # Execute the query to fetch the updated user list
                        mysql_cursor.execute("SELECT username FROM users")
                        # Fetch all the usernames from the result
                        rows = mysql_cursor.fetchall()
                        updated_users = ','.join([row[0] for row in rows])
                        mysql_cursor.execute("SELECT friends, friend_requests FROM users WHERE username = %s",
                                             (self.username,))
                        row = mysql_cursor.fetchone()
                        self.friends = [] if row[0] is None else row[0].split(',')
                        self.friend_requests = [] if row[1] is None else row[1].split(',')
                        friends = ','.join(self.friends)
                        friend_requests = ','.join(self.friend_requests)
                        sharing_read_only = ','.join(get_sharing_read_only(self.username))
                        sharing_read_write = ','.join(get_sharing_read_write(self.username))
                        shared_read_only = ','.join(get_shared_read_only(self.username))
                        shared_read_write = ','.join(get_shared_read_write(self.username))
                        message = f"{updated_users}||{friends}||{friend_requests}||{sharing_read_only}||" \
                                  f"{sharing_read_write}||{shared_read_only}||{shared_read_write}"
                        send_data(self.client_socket, message)
                    except Exception as error:
                        print(error)

            elif data.startswith("add_friend"):
                new_friend = data.split()[1]
                self.friends.append(new_friend)
                friends = ','.join(self.friends)
                mysql_cursor.execute("SELECT friends FROM users WHERE username = %s", (new_friend,))
                row = mysql_cursor.fetchone()
                add_to_new_friend = row[0] + ',' + self.username if row[0] is not None else self.username
                mysql_cursor.execute("UPDATE users SET friends = %s WHERE username = %s", (friends, self.username))
                mysql_cursor.execute("UPDATE users SET friends = %s WHERE username = %s",
                                     (add_to_new_friend, new_friend))
                mysql_connection.commit()
                print(f"{self.username} has added {new_friend} as a friend")
            elif data.startswith("send_friend_request"):
                user = data.split('||')[1]
                mysql_cursor.execute("SELECT friend_requests FROM users WHERE username = %s", (user,))
                row = mysql_cursor.fetchone()
                check_requests = row[0].split(',') if row[0] is not None else []
                if self.username not in check_requests:
                    if row[0] is None:
                        friend_requests = self.username
                    else:
                        friend_requests = row[0] + ',' + self.username
                    mysql_cursor.execute("UPDATE users SET friend_requests = %s WHERE username = %s",
                                         (friend_requests, user))
                    mysql_connection.commit()
                    print(f"{self.username} has sent {user} a friend request")
                    send_data(self.client_socket, "OK")
                else:
                    send_data(self.client_socket, "You've already sent this user a friend request")
            elif data.startswith("remove_friend_request"):
                user = data.split('||')[1]
                self.friend_requests.remove(user)
                friend_requests = ','.join(self.friend_requests) if self.friend_requests else None
                mysql_cursor.execute("UPDATE users SET friend_requests = %s WHERE username = %s",
                                     (friend_requests, self.username))
                mysql_connection.commit()
            elif data.startswith("remove_friend"):
                friend = data.split("||")[1]
                self.friends.remove(friend)
                friends = ','.join(self.friends) if self.friends else None
                mysql_cursor.execute("SELECT friends FROM users WHERE username = %s", (friend,))
                row = mysql_cursor.fetchone()
                removed_friend_friends = row[0].split(',')
                removed_friend_friends.remove(self.username)
                removed_friend_friends = ','.join(removed_friend_friends) if removed_friend_friends else None
                mysql_cursor.execute("UPDATE users SET friends = %s WHERE username = %s", (friends, self.username))
                mysql_cursor.execute("UPDATE users SET friends = %s WHERE username = %s",
                                     (removed_friend_friends, friend))
                mysql_connection.commit()
                print(f"{self.username} and {friend} are no longer friends")
            elif data.startswith("share"):
                shared_user = data.split("||")[1]
                permissions = data.split("||")[2]
                if shared_user in get_users_user_is_sharing_with(self.username):
                    remove_row(self.username, shared_user)
                if permissions != "remove":
                    insert_user_sharing(self.username, shared_user, permissions)
                print(f"{self.username} has shared his folder with {shared_user} with {permissions} permissions")
                print(f"{self.username} is currently sharing to {get_users_user_is_sharing_with(self.username)}")
            elif data.startswith("request_commands"):
                if self.username in waiting_commands:
                    commands = dumps(waiting_commands[self.username])
                    send_data(self.client_socket, commands, send_bytes=True)
                    waiting_commands[self.username] = []
                else:
                    commands = dumps([])
                    send_data(self.client_socket, commands, send_bytes=True)

            else:
                send_data(self.client_socket, "Invalid command")


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


def get_users_user_is_sharing_with(username):
    """
        Retrieves a list of users that the given username is sharing with.

        :param username: The username for which the shared users are retrieved.
        :return: A list of users that the given username is sharing with.
        :raises mysql.connector.Error: If there is an error retrieving the shared users from the database.
        """
    try:
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()
        query = "SELECT shared_user FROM users_sharing WHERE sharing_user = %s"
        values = (username,)
        mysql_cursor.execute(query, values)
        rows = mysql_cursor.fetchall()
        mysql_connection.close()
        users_list = []
        for row in rows:
            users_list.append(row[0])
        return users_list
    except mysql.connector.Error as error:
        print(f"Error retrieving users {username} is sharing with: {error}")


def get_users_sharing_with_user(username):
    try:
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()
        query = "SELECT sharing_user, permission FROM users_sharing WHERE shared_user = %s"
        values = (username,)
        mysql_cursor.execute(query, values)
        rows = mysql_cursor.fetchall()
        mysql_connection.close()
        users_list = []
        for row in rows:
            users_list.append(row[0])
        return users_list
    except mysql.connector.Error as error:
        print(f"Error retrieving users sharing with {username}: {error}")


def insert_user_sharing(sharing_user, shared_user, permission):
    try:
        # Connect to the database
        mysql_connection = mysql.connector.connect(**database_config)
        mysql_cursor = mysql_connection.cursor()

        query = "INSERT INTO users_sharing (sharing_user, shared_user, permission) VALUES (%s, %s, %s)"
        values = (sharing_user, shared_user, permission)
        mysql_cursor.execute(query, values)
        mysql_connection.commit()
        mysql_connection.close()
        print("User sharing information inserted successfully.")
        return True

    except mysql.connector.Error as error:
        print(f"Error inserting user sharing information: {error}")


def remove_row(sharing_user, shared_user):
    # Establish a connection to the MySQL server
    mysql_connection = mysql.connector.connect(**database_config)
    mysql_cursor = mysql_connection.cursor()
    try:
        # Create a cursor object to execute SQL queries
        mysql_cursor = mysql_connection.cursor()

        # Prepare the DELETE statement
        delete_query = "DELETE FROM users_sharing WHERE sharing_user = %s AND shared_user = %s"

        # Execute the DELETE statement with the username as a parameter
        mysql_cursor.execute(delete_query, (sharing_user, shared_user))

        # Commit the changes to the database
        mysql_connection.commit()

        # Print a message to indicate successful deletion
        print("Row deleted successfully")

    except mysql.connector.Error as error:
        # Handle any potential errors
        print(f"Error deleting row: {error}")

    finally:
        # Close the cursor and connection
        mysql_cursor.close()
        mysql_connection.close()


def get_permissions(sharing_user, shared_user):
    # Establish a connection to the MySQL server
    mysql_connection = mysql.connector.connect(**database_config)
    mysql_cursor = mysql_connection.cursor()
    try:
        # Create a cursor object to execute SQL queries
        mysql_cursor = mysql_connection.cursor()
        # Prepare the SELECT statement
        select_query = "SELECT permission FROM users_sharing WHERE sharing_user = %s AND shared_user = %s"
        # Execute the SELECT statement with the sharing_user and shared_user as parameters
        mysql_cursor.execute(select_query, (sharing_user, shared_user))
        # Fetch the first row returned by the query
        row = mysql_cursor.fetchone()
        if row:
            # Return the value of the 'permissions' column
            return row[0]
        else:
            # Return a default value if no matching row is found
            return None
    except mysql.connector.Error as error:
        # Handle any potential errors
        print(f"Error retrieving permissions: {error}")
    finally:
        # Close the cursor and connection
        mysql_cursor.close()
        mysql_connection.close()


def get_sharing_read_only(username):
    sharing_read_only = []
    users = get_users_user_is_sharing_with(username)
    for shared_user in users:
        if get_permissions(username, shared_user) == "read":
            sharing_read_only.append(shared_user)
    return sharing_read_only


def get_sharing_read_write(username):
    sharing_read_write = []
    users = get_users_user_is_sharing_with(username)
    for shared_user in users:
        if get_permissions(username, shared_user) == "read_write":
            sharing_read_write.append(shared_user)
    return sharing_read_write


def get_shared_read_only(username):
    shared_read_only = []
    users = get_users_sharing_with_user(username)
    for sharing_user in users:
        if get_permissions(sharing_user, username) == "read":
            shared_read_only.append(sharing_user)
    return shared_read_only


def get_shared_read_write(username):
    shared_read_write = []
    users = get_users_sharing_with_user(username)
    for sharing_user in users:
        if get_permissions(sharing_user, username) == "read_write":
            shared_read_write.append(sharing_user)
    return shared_read_write


def add_to_waiting_commands(users, command):
    """
    Adds a command to the waiting commands for each user.

    :param users: A list of users.
    :param command: The command to be added to the waiting commands.
    :returns: None
    """
    for user in users:
        if user in connected_users:
            if user in waiting_commands:
                waiting_commands[user].append(command)
            else:
                waiting_commands[user] = [command]


def update_command(command, username, modified_folder):
    """
    Adds the command that was given by the user to the list of commands of each user that has any permission to the
    modified folder.

    :param command: The command to be added.
    :param username: The user that sent the command.
    :param modified_folder: The folder that was modified.
    :returns: None
    """
    if modified_folder == username:
        add_to_waiting_commands(get_users_user_is_sharing_with(username), command)
    else:
        users = get_users_user_is_sharing_with(modified_folder)
        users.remove(username)
        users.append(modified_folder)
        add_to_waiting_commands(users, command)
