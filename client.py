# TODO update file changes - watcher for Read And Write directory
# TODO when adding a friend, the folders don't update until the client is reopened
import hashlib
import os
import pathlib
import shutil
import socket
import threading
import time
from pickle import loads, dumps
import rsa
from cryptography.fernet import Fernet, InvalidToken
from login_window import UiLogin
from signup_window import UiSignup
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QFileSystemModel, QInputDialog, QMessageBox, \
    QPushButton
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QFileSystemWatcher
import sys
from file_classes import File, Directory
from main_window import Ui_MainWindow

SERVER_IP = '127.0.0.1'
PORT = 8080
DIRECTORY = "./FS/Folders"
FOLDER = "Folders"
READ_ONLY_SHARES = "./FS/Read Only"
READ_WRITE_SHARES = "./FS/Read and Write"
CHUNK_SIZE = 4096
KEYS_TO_DISABLE = [Qt.Key_Space, Qt.Key_Period, Qt.Key_Slash, Qt.Key_Comma, Qt.Key_Semicolon, Qt.Key_Colon, Qt.Key_Bar,
                   Qt.Key_Backslash, Qt.Key_BracketLeft, Qt.Key_BracketRight, Qt.Key_ParenLeft, Qt.Key_ParenRight,
                   Qt.Key_BraceLeft, Qt.Key_BraceRight, Qt.Key_Apostrophe, Qt.Key_QuoteDbl, Qt.Key_Equal, Qt.Key_Plus,
                   Qt.Key_Minus, Qt.Key_Percent]
REFRESH_FREQUENCY = 5
HEADER_SIZE = 10
NO_FRIENDS = "No Friends Added"
NO_FRIEND_REQUESTS = "No Friend Requests"


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


def disable_keys(field):
    field.keyPressEvent = lambda event: event.ignore() if event.key() in KEYS_TO_DISABLE else QLineEdit.keyPressEvent(
        field, event)


def delete_item(item_path):
    if os.path.isfile(item_path):
        # Delete a file
        os.remove(item_path)
    elif os.path.isdir(item_path):
        # Delete a folder and its contents
        shutil.rmtree(item_path)


# Example function to rename a file or folder
def rename_item(item_path, new_name):
    try:
        new_path = os.path.join(os.path.dirname(item_path), new_name)
        os.rename(item_path, new_path)
    except Exception as err:
        QMessageBox.warning(widget, "Error", err.args[1])


def create_fail_label(parent, text, geometry):
    fail_label = QtWidgets.QLabel(parent)
    fail_label.setGeometry(geometry)
    fail_label.setText(text)
    fail_label.hide()
    font = QtGui.QFont()
    font.setPointSize(11)
    fail_label.setFont(font)
    fail_label.setStyleSheet("color: rgb(255, 0, 0)")
    return fail_label


def open_file(item_path):
    # Open the item (assuming it's a file)
    if os.path.isfile(item_path):
        # Open the file using the default system application
        os.startfile(item_path)


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self, dir_path):
        super().__init__()
        self.lock = threading.Lock()
        self.exit = False
        self.copied_item_path = None
        self.cut_item_path = None
        self.dir_path = dir_path
        self.username = os.path.basename(dir_path)
        self.read_write_path = os.path.join(READ_WRITE_SHARES, self.username)
        self.read_only_path = os.path.join(READ_ONLY_SHARES, self.username)
        self.file_timestamps = {}
        self.directory_history = []  # List to store directory history
        self.read_write_directory_history = [self.read_write_path]
        self.read_only_directory_history = [self.read_only_path]
        self.users = []
        self.friends = []
        self.friend_requests = []
        self.sharing_read_only = []
        self.sharing_read_write = []
        self.shared_read_only = []
        self.shared_read_write = []
        os.makedirs(self.read_only_path, exist_ok=True)
        os.makedirs(self.read_write_path, exist_ok=True)
        self.setupUi(self)
        self.setWindowTitle("FileSpace")
        self.model = QFileSystemModel()
        self.model.setRootPath(dir_path)
        self.list_view.setModel(self.model)
        self.list_view.setRootIndex(self.model.index(dir_path))
        self.list_view.setIconSize(QtCore.QSize(32, 32))
        self.list_view.setGridSize(QtCore.QSize(96, 96))
        self.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.set_initial_directory()
        self.tabs.setCurrentIndex(0)
        self.upload_files_button.clicked.connect(
            lambda: self.upload_files(self.model))  # Connect the upload button to the method
        self.upload_folders_button.clicked.connect(lambda: self.upload_folders(self.model))
        self.list_view.doubleClicked.connect(self.on_list_view_double_clicked)
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(lambda event: self.create_context_menu(event, self.list_view))
        self.go_back_button.hide()
        self.go_back_button.clicked.connect(self.go_back)
        self.rw_go_back_button.hide()
        self.rw_go_back_button.clicked.connect(self.rw_go_back)
        self.r_go_back_button.hide()
        self.r_go_back_button.clicked.connect(self.r_go_back)
        self.upload_files_shares_button.hide()
        self.upload_files_shares_button.clicked.connect(lambda: self.upload_files(self.read_write_model))
        self.upload_folders_shares_button.hide()
        self.upload_folders_shares_button.clicked.connect(lambda: self.upload_folders(self.read_write_model))
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.dir_path)
        self.recursively_add_paths(self.dir_path)  # Add subdirectories to watcher recursively
        self.watcher.fileChanged.connect(self.file_changed)

        self.friends_list_widget.itemDoubleClicked.connect(self.friend_double_clicked)
        self.friend_requests_list_widget.itemDoubleClicked.connect(self.friend_request_double_clicked)
        self.sharing_read_write_list_widget.itemDoubleClicked.connect(self.sharing_to_double_clicked)
        self.sharing_read_only_list_widget.itemDoubleClicked.connect(self.sharing_to_double_clicked)
        self.search_bar.textChanged.connect(self.search_users)
        self.search_results_list.itemDoubleClicked.connect(self.user_double_clicked)
        refreshes_thread = threading.Thread(target=self.handle_refreshes)
        refreshes_thread.start()
        receive_commands_thread = threading.Thread(target=self.handle_waiting_commands)
        receive_commands_thread.start()
        self.get_shared_folders()
        self.read_only_model = QFileSystemModel()
        self.read_only_model.setRootPath(self.read_only_path)
        self.read_only_list_view.setModel(self.read_only_model)
        self.read_only_list_view.setRootIndex(self.read_only_model.index(self.read_only_path))
        self.read_only_list_view.doubleClicked.connect(self.on_read_only_list_view_double_clicked)
        self.read_write_model = QFileSystemModel()
        self.read_write_model.setRootPath(self.read_write_path)
        self.read_write_list_view.setModel(self.read_write_model)
        self.read_write_list_view.setRootIndex(self.read_write_model.index(self.read_write_path))
        self.read_write_list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.read_write_list_view.customContextMenuRequested.connect(
            lambda event: self.create_context_menu(event, self.read_write_list_view))
        self.read_write_list_view.doubleClicked.connect(self.on_read_write_list_view_double_clicked)

    def get_shared_folders(self):
        with self.lock:
            send_data(client_socket, "get_shared_folders")
            num = int(receive_data(client_socket))
            for i in range(num):
                dir_data = receive_data(client_socket, return_bytes=True)
                folder = loads(dir_data)
                if folder.name in self.shared_read_write:
                    folder.create(os.path.join(self.read_write_path, folder.name))
                elif folder.name in self.shared_read_only:
                    folder.create(os.path.join(self.read_only_path, folder.name))

    def handle_waiting_commands(self):
        while not self.exit:
            self.receive_commands()
            time.sleep(REFRESH_FREQUENCY)

    def handle_refreshes(self):
        while not self.exit:
            self.refresh()
            time.sleep(REFRESH_FREQUENCY)

    def receive_commands(self):
        """
            Receives and processes current user's waiting commands from the server.

            :returns: None
            """
        try:
            with self.lock:
                send_data(client_socket, "request_commands")
                serialized_commands = receive_data(client_socket, return_bytes=True)
                commands = loads(serialized_commands)
                for command in commands:
                    if type(command) is tuple:
                        if command[0].startswith("upload_dir"):
                            rel_path = command[0].split("||")[-1].strip()  # Extract the relative path
                            serialized_dir = command[1]
                            directory = loads(serialized_dir)
                            if pathlib.Path(rel_path).parts[0] == self.username:
                                location = os.path.join(DIRECTORY, rel_path)  # If the modified folder is owned by
                                # the user, use the user's main directory
                            else:
                                if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                    location = os.path.join(self.read_write_path, rel_path)  # If the modified folder
                                    # is in the shared read-write list, use the read-write path
                                else:
                                    location = os.path.join(self.read_only_path, rel_path)  # Otherwise, use the
                                    # read-only path
                            print(location)
                            directory.create(location)  # Create the directory at the specified location
                        elif command[0].startswith("upload_file"):
                            rel_path = command[0].split("||")[-1].strip()
                            serialized_file = command[1]
                            file = loads(serialized_file)
                            if pathlib.Path(rel_path).parts[0] == self.username:
                                location = os.path.join(DIRECTORY, rel_path)
                            else:
                                if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                    location = os.path.join(self.read_write_path, rel_path)
                                else:
                                    location = os.path.join(self.read_only_path, rel_path)
                            print(location)
                            directory.create(file)
                        elif command[0].startswith("file_edit"):
                            rel_path = command[0].split("||")[-1]
                            file_data = command[1]
                            if pathlib.Path(rel_path).parts[0] == self.username:
                                file_path = os.path.join(DIRECTORY, rel_path)
                            else:
                                if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                    file_path = os.path.join(self.read_write_path, rel_path)
                                else:
                                    file_path = os.path.join(self.read_only_path, rel_path)
                            with open(file_path, "wb") as f:
                                f.write(file_data)
                    elif command.startswith("delete_item"):
                        rel_path = command.split("||")[1].strip()
                        if pathlib.Path(rel_path).parts[0] == self.username:
                            item_path = os.path.join(DIRECTORY, rel_path)
                        else:
                            if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                item_path = os.path.join(self.read_write_path, rel_path)
                            else:
                                item_path = os.path.join(self.read_only_path, rel_path)
                        delete_item(item_path)
                        print(f"Deleted {item_path}")
                    elif command.startswith("rename_item"):
                        rel_path = command.split("||")[1].strip()
                        print(os.path.join(self.read_write_path, rel_path))
                        if pathlib.Path(rel_path).parts[0] == self.username:
                            item_path = os.path.join(DIRECTORY, rel_path)
                        else:
                            if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                item_path = os.path.join(self.read_write_path, rel_path)
                            else:
                                item_path = os.path.join(self.read_only_path, rel_path)
                        new_name = command.split("||")[-1].strip()

                        rename_item(item_path, new_name)
                        print(f"Renamed {item_path} to {new_name}")
                    elif command.startswith("create_file"):
                        rel_path = command.split("||")[1].strip()
                        if pathlib.Path(rel_path).parts[0] == self.username:
                            new_file_path = os.path.join(DIRECTORY, rel_path)
                        else:
                            if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                new_file_path = os.path.join(self.read_write_path, rel_path)
                            else:
                                new_file_path = os.path.join(self.read_only_path, rel_path)
                        if os.path.exists(new_file_path):
                            return
                            # Create the new file
                        with open(new_file_path, 'w'):
                            pass  # Do nothing, just create an empty file
                        print(f"File {new_file_path} created")
                    elif command.startswith("create_folder"):
                        rel_path = command.split("||")[1].strip()
                        if pathlib.Path(rel_path).parts[0] == self.username:
                            new_dir_path = os.path.join(DIRECTORY, rel_path)
                        else:
                            if pathlib.Path(rel_path).parts[0] in self.shared_read_write:
                                new_dir_path = os.path.join(self.read_write_path, rel_path)
                            else:
                                new_dir_path = os.path.join(self.read_only_path, rel_path)
                        os.makedirs(new_dir_path, exist_ok=True)
                        print(f"Folder {new_dir_path} created")
                    elif command.startswith("copy"):
                        rel_copied_item_path = command.split("||")[1]
                        rel_destination_path = command.split("||")[2]
                        if pathlib.Path(rel_copied_item_path).parts[0] == self.username:
                            copied_item_path = os.path.join(DIRECTORY, rel_copied_item_path)
                            destination_path = os.path.join(DIRECTORY, rel_destination_path)
                        else:
                            if pathlib.Path(rel_copied_item_path).parts[0] in self.shared_read_write:
                                copied_item_path = os.path.join(self.read_write_path, rel_copied_item_path)
                                destination_path = os.path.join(self.read_write_path, rel_destination_path)
                            else:
                                copied_item_path = os.path.join(self.read_only_path, rel_copied_item_path)
                                destination_path = os.path.join(self.read_only_path, rel_destination_path)

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

                    elif command.startswith("move"):
                        rel_cut_item_path = command.split("||")[1]
                        rel_destination_path = command.split("||")[2]
                        if pathlib.Path(rel_cut_item_path).parts[0] == self.username:
                            cut_item_path = os.path.join(DIRECTORY, rel_cut_item_path)
                            destination_path = os.path.join(DIRECTORY, rel_destination_path)
                        else:
                            if pathlib.Path(rel_cut_item_path).parts[0] in self.shared_read_write:
                                cut_item_path = os.path.join(self.read_write_path, rel_cut_item_path)
                                destination_path = os.path.join(self.read_write_path, rel_destination_path)
                            else:
                                cut_item_path = os.path.join(self.read_only_path, rel_cut_item_path)
                                destination_path = os.path.join(self.read_only_path, rel_destination_path)
                        try:
                            # Move the file or folder
                            shutil.move(cut_item_path, destination_path)
                            print(f"Moved {cut_item_path} to {destination_path}")
                        except shutil.Error:
                            pass
                print(f"commands:{commands}")
        except OSError as err:
            print(err)
            self.exit = True

    def refresh(self):
        try:
            with self.lock:
                send_data(client_socket, "refresh")
                data = receive_data(client_socket)
                self.users = data.split('||')[0].split(',')
                self.users.remove(os.path.basename(self.dir_path))
                friends = data.split('||')[1].split(',')
                friend_requests = data.split('||')[2].split(',')
                sharing_read = data.split('||')[3].split(',')
                sharing_rw = data.split('||')[4].split(',')
                self.sharing_read_only = sharing_read if sharing_read != [''] else []
                self.sharing_read_write = sharing_rw if sharing_rw != [''] else []
                shared_read = data.split('||')[5].split(',')
                shared_rw = data.split('||')[6].split(',')
                self.shared_read_only = shared_read if shared_read != [''] else []
                self.shared_read_write = shared_rw if shared_rw != [''] else []
                self.friends = friends if friends[0] else []
                self.friend_requests = friend_requests if friend_requests[0] else []
                self.friends_list_widget.clear()
                if not self.friends:
                    self.friends_list_widget.addItem(NO_FRIENDS)
                else:
                    self.friends_list_widget.addItems(self.friends)
                self.friend_requests_list_widget.clear()
                if not self.friend_requests:
                    self.friend_requests_list_widget.addItem(NO_FRIEND_REQUESTS)
                else:
                    self.friend_requests_list_widget.addItems(self.friend_requests)
                self.sharing_read_write_list_widget.clear()
                if self.sharing_read_write:
                    self.sharing_read_write_list_widget.addItems(self.sharing_read_write)
                self.sharing_read_only_list_widget.clear()
                if self.sharing_read_only:
                    self.sharing_read_only_list_widget.addItems(self.sharing_read_only)
                for folder in os.listdir(self.read_write_path):
                    if folder in self.shared_read_only:
                        f = Directory(os.path.join(self.read_write_path, folder))
                        f.change_path(os.path.join(self.read_only_path, folder))
                    elif folder not in self.shared_read_write:
                        shutil.rmtree(os.path.join(self.read_write_path, folder))
                for folder in os.listdir(self.read_only_path):
                    if folder in self.shared_read_write:
                        f = Directory(os.path.join(self.read_only_path, folder))
                        f.change_path(os.path.join(self.read_write_path, folder))
                    elif folder not in self.shared_read_only:
                        shutil.rmtree(os.path.join(self.read_only_path, folder))

        except OSError:
            self.exit = True

    def friend_double_clicked(self, item):
        friend_name = item.text()  # Assuming the item is a QListWidgetItem
        if friend_name == NO_FRIENDS:
            return
        # Create a dialog box
        dialog = QMessageBox()
        dialog.setWindowTitle("Friend Details")
        dialog.setText(f"Friend: {friend_name}")

        # Add share and remove buttons
        share_button = dialog.addButton("Share", QMessageBox.ActionRole)
        remove_button = dialog.addButton("Remove Friend", QMessageBox.ActionRole)

        # Add a cancel button
        cancel_button = dialog.addButton(QMessageBox.Cancel)

        # Disable the default OK button
        dialog.setDefaultButton(cancel_button)

        # Execute the dialog and handle the button clicked event
        dialog.exec_()

        clicked_button = dialog.clickedButton()
        if clicked_button == share_button:
            # Share button clicked, call self.share_friend
            self.share_friend(friend_name)
        elif clicked_button == remove_button:
            # Remove friend button clicked, call self.remove_friend
            self.remove_friend(friend_name)
        elif clicked_button == cancel_button:
            # Cancel button clicked, do nothing or perform any required cleanup
            print("Canceled")

    def share_friend(self, friend_name):
        # Create a Directory object to be shared
        directory = Directory(self.dir_path)
        if friend_name in self.sharing_read_write:
            self.change_permission(friend_name, "read_write")
            return
        elif friend_name in self.sharing_read_only:
            self.change_permission(friend_name, "read")
            return
        # Show a pop-up message box to ask for permissions
        message_box = QMessageBox()
        message_box.setWindowTitle("Permission Selection")
        message_box.setText(f"What permissions would you like to give {friend_name}?")

        # Add buttons for read, write, and cancel options
        read_button = QPushButton("Read Only")
        write_button = QPushButton("Read And Write")
        cancel_button = QPushButton("Cancel")
        message_box.addButton(read_button, QMessageBox.ButtonRole.AcceptRole)
        message_box.addButton(write_button, QMessageBox.ButtonRole.AcceptRole)
        message_box.addButton(cancel_button, QMessageBox.ButtonRole.RejectRole)
        message_box.setDefaultButton(cancel_button)
        # Execute the message box and get the selected button
        clicked_button = message_box.exec_()
        # Process the selected button
        if clicked_button == 0:
            print(f"Sharing read-only with friend: {friend_name}")
            self.sharing_read_only.append(friend_name)
            self.sharing_read_only_list_widget.clear()
            self.sharing_read_only_list_widget.addItems(self.sharing_read_only)
            send_data(client_socket, f"share||{friend_name}||read")
        elif clicked_button == 1:
            print(f"Sharing read-write with friend: {friend_name}")
            self.sharing_read_write.append(friend_name)
            self.sharing_read_write_list_widget.clear()
            self.sharing_read_write_list_widget.addItems(self.sharing_read_write)
            send_data(client_socket, f"share||{friend_name}||read_write")

        else:
            print("Share canceled")

    def change_permission(self, shared_user, current_perm):
        message_box = QMessageBox()
        message_box.setWindowTitle("Change Permission")
        message_box.setText(f"{shared_user} currently has {current_perm} permissions.\nWould you like to change them?")
        if current_perm == "read_write":
            # Add buttons for read, write, and cancel options
            read_button = QPushButton("Read Only")
            message_box.addButton(read_button, QMessageBox.ButtonRole.AcceptRole)
        elif current_perm == "read":
            write_button = QPushButton("Read And Write")
            message_box.addButton(write_button, QMessageBox.ButtonRole.AcceptRole)
        remove_perms_button = QPushButton("Remove Permissions")
        cancel_button = QPushButton("Cancel")
        message_box.addButton(remove_perms_button, QMessageBox.ButtonRole.RejectRole)
        message_box.addButton(cancel_button, QMessageBox.ButtonRole.RejectRole)
        message_box.setDefaultButton(cancel_button)
        # Execute the message box and get the selected button
        clicked_button = message_box.exec_()
        if clicked_button == 0:
            if current_perm == "read_write":
                self.sharing_read_write_list_widget.takeItem(self.sharing_read_write.index(shared_user))
                self.sharing_read_write.remove(shared_user)
                self.sharing_read_only.append(shared_user)
                self.sharing_read_only_list_widget.addItem(shared_user)
                send_data(client_socket, f"share||{shared_user}||read")
                print(f"Changed {shared_user}'s permissions from read and write to read only")
            else:
                self.sharing_read_only_list_widget.takeItem(self.sharing_read_only.index(shared_user))
                self.sharing_read_only.remove(shared_user)
                self.sharing_read_write.append(shared_user)
                self.sharing_read_write_list_widget.addItem(shared_user)
                send_data(client_socket, f"share||{shared_user}||read_write")
                print(f"Changed {shared_user}'s permissions from read only to read and write")

        elif clicked_button == 1:
            if current_perm == "read_write":
                self.sharing_read_write_list_widget.takeItem(self.sharing_read_write.index(shared_user))
                self.sharing_read_write.remove(shared_user)
                send_data(client_socket, f"share||{shared_user}||remove")
                print(f"Removed permissions for {shared_user}")
            else:
                self.sharing_read_only_list_widget.takeItem(self.sharing_read_only.index(shared_user))
                self.sharing_read_only.remove(shared_user)
                send_data(client_socket, f"share||{shared_user}||remove")
                print(f"Removed permissions for {shared_user}")

    def sharing_to_double_clicked(self, item):
        user = item.text()
        if user in self.sharing_read_write:
            self.change_permission(user, "read_write")
        else:
            self.change_permission(user, "read")

    def remove_friend(self, friend_name):
        if friend_name == NO_FRIENDS:
            return
        print(f"Removing friend: {friend_name}")
        self.friends.remove(friend_name)
        if self.friends:
            index = self.friends_list_widget.currentRow()
            self.friends_list_widget.takeItem(index)
        else:
            self.friends_list_widget.clear()
            self.friends_list_widget.addItem(NO_FRIENDS)
        send_data(client_socket, f"remove_friend ||{friend_name}")

    def send_friend_request(self, user):
        if user not in self.friends:
            send_data(client_socket, f"send_friend_request||{user}")
            print(f"Sent a friend request to {user}")
            response = receive_data(client_socket)
        else:
            response = "This user is already your friend"
        return response

    def user_double_clicked(self, item):
        user = item.text()
        message_box = QMessageBox()
        message_box.setWindowTitle("Send Friend Request")
        message_box.setText(f"Send {user} a friend request?")

        # Add buttons for Yes and No options
        message_box.addButton(QMessageBox.Yes)
        message_box.addButton(QMessageBox.No)

        # Execute the message box and get the result
        result = message_box.exec_()
        if result == QMessageBox.Yes:
            response = self.send_friend_request(user)
            if response != "OK":
                QMessageBox.warning(self, "Error", response)

    def add_friend(self, user):
        self.friends.append(user)
        self.friends_list_widget.clear()
        self.friends_list_widget.addItems(self.friends)
        send_data(client_socket, f"add_friend {user}")
        print(f"added {user}")

    def remove_friend_request(self, user):
        self.friend_requests.remove(user)
        if self.friend_requests:
            index = self.friend_requests_list_widget.currentRow()
            self.friend_requests_list_widget.takeItem(index)
        else:
            self.friend_requests_list_widget.clear()
            self.friend_requests_list_widget.addItem(NO_FRIEND_REQUESTS)
        send_data(client_socket, f"remove_friend_request ||{user}")

    def friend_request_double_clicked(self, item):
        user = item.text()
        if user == NO_FRIEND_REQUESTS:
            return
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle("Add Friend")
        dialog.setText(f"Add {user} as a friend?")
        dialog.addButton(QtWidgets.QPushButton("Yes"), QMessageBox.YesRole)
        dialog.addButton(QtWidgets.QPushButton("No"), QMessageBox.ActionRole)
        dialog.addButton(QtWidgets.QPushButton("Close"), QMessageBox.ActionRole)

        dialog.exec_()
        button = dialog.clickedButton().text()

        if button != "Close":
            self.remove_friend_request(user)
            if button == "Yes":
                self.add_friend(user)

    def search_users(self, search_text):
        if not search_text:
            # Clear the current contents of the search results list widget
            self.search_results_list.clear()
        else:
            self.search_results_list.clear()
            # Filter the users list based on the search text
            filtered_users = [user for user in self.users if search_text.lower() in user.lower()]

            # Display the matching results in the search results list widget
            self.search_results_list.addItems(filtered_users)

    def recursively_add_paths(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                path = os.path.join(root, file)
                self.watcher.addPath(path)
                self.file_timestamps[path] = os.path.getmtime(path)

    def file_changed(self, path):
        if not os.path.exists(path):
            # File doesn't exist anymore, skip processing
            return

        current_timestamp = os.path.getmtime(path)
        previous_timestamp = self.file_timestamps.get(path)
        os.path.getmtime(path)
        if previous_timestamp and current_timestamp != previous_timestamp:
            print("File edited:", path)
            file_data = File(path).data
            file_size = File(path).size
            # Send the file path and its data over the socket
            send_data(client_socket, f"file_edit ||{os.path.relpath(path, DIRECTORY)}")
            send_data(client_socket, file_data, send_bytes=True)

        self.file_timestamps[path] = current_timestamp

    def on_list_view_double_clicked(self, index):
        # Check if the selected index represents a directory
        if self.model.isDir(index):
            # Get the path of the double-clicked directory
            directory_path = self.model.filePath(index)
            # Set the root path of the model to the double-clicked directory
            self.model.setRootPath(directory_path)
            # Set the root index of the list view to the new root path
            self.list_view.setRootIndex(self.model.index(directory_path))
            self.go_back_button.show()
            self.directory_history.append(directory_path)
        else:
            file_path = self.model.filePath(index)
            open_file(file_path)

    def on_read_write_list_view_double_clicked(self, index):
        # Check if the selected index represents a directory
        if self.read_write_model.isDir(index):
            # Get the path of the double-clicked directory
            directory_path = self.read_write_model.filePath(index)
            # Set the root path of the model to the double-clicked directory
            self.read_write_model.setRootPath(directory_path)
            # Set the root index of the list view to the new root path
            self.read_write_list_view.setRootIndex(self.read_write_model.index(directory_path))
            self.rw_go_back_button.show()
            self.upload_files_shares_button.show()
            self.upload_folders_shares_button.show()
            self.read_write_directory_history.append(directory_path)
        else:
            file_path = self.read_write_model.filePath(index)
            open_file(file_path)

    def on_read_only_list_view_double_clicked(self, index):
        # Check if the selected index represents a directory
        if self.read_only_model.isDir(index):
            # Get the path of the double-clicked directory
            directory_path = self.read_only_model.filePath(index)
            # Set the root path of the model to the double-clicked directory
            self.read_only_model.setRootPath(directory_path)
            # Set the root index of the list view to the new root path
            self.read_only_list_view.setRootIndex(self.read_only_model.index(directory_path))
            self.r_go_back_button.show()
            self.read_only_directory_history.append(directory_path)
        else:
            file_path = self.read_only_model.filePath(index)
            open_file(file_path)

    def go_back(self):
        if len(self.directory_history) >= 1:
            # Remove the current directory from the history
            self.directory_history.pop()
            # Get the previous directory path
            parent_directory_path = self.directory_history[-1]
            # Set the root path of the model to the parent directory
            self.model.setRootPath(parent_directory_path)
            # Set the root index of the list view to the new root path
            self.list_view.setRootIndex(self.model.index(parent_directory_path))

        # Show or hide the "Go Back" button based on the directory history
        if len(self.directory_history) <= 1:
            self.go_back_button.hide()
        else:
            self.go_back_button.show()

    def rw_go_back(self):
        if len(self.read_write_directory_history) >= 1:
            # Remove the current directory from the history
            self.read_write_directory_history.pop()
            # Get the previous directory path
            parent_directory_path = self.read_write_directory_history[-1]
            # Set the root path of the model to the parent directory
            self.read_write_model.setRootPath(parent_directory_path)
            # Set the root index of the list view to the new root path
            self.read_write_list_view.setRootIndex(self.read_write_model.index(parent_directory_path))

        # Show or hide the "Go Back" button based on the directory history
        if len(self.read_write_directory_history) <= 1:
            self.rw_go_back_button.hide()
            self.upload_files_shares_button.hide()
            self.upload_folders_shares_button.hide()
        else:
            self.rw_go_back_button.show()
            self.upload_files_shares_button.show()
            self.upload_folders_shares_button.show()

    def r_go_back(self):
        if len(self.read_only_directory_history) >= 1:
            # Remove the current directory from the history
            self.read_only_directory_history.pop()
            # Get the previous directory path
            parent_directory_path = self.read_only_directory_history[-1]
            # Set the root path of the model to the parent directory
            self.read_only_model.setRootPath(parent_directory_path)
            # Set the root index of the list view to the new root path
            self.read_only_list_view.setRootIndex(self.read_only_model.index(parent_directory_path))

        # Show or hide the "Go Back" button based on the directory history
        if len(self.read_only_directory_history) <= 1:
            self.r_go_back_button.hide()
        else:
            self.r_go_back_button.show()

    def update_directory_history(self, directory_path):
        # Add the current directory path to the history
        self.directory_history.append(directory_path)

    def set_initial_directory(self):
        self.model.setRootPath(self.dir_path)
        self.list_view.setRootIndex(self.model.index(self.dir_path))
        self.directory_history.append(self.dir_path)

    def copy_files_or_folders(self, paths, destination_path):
        for path in paths:
            if os.path.isfile(path):
                # Copy a file
                shutil.copy2(path, destination_path)
            elif os.path.isdir(path):
                # Copy a folder
                folder_name = os.path.basename(path)
                destination_folder_path = os.path.join(destination_path, folder_name)
                shutil.copytree(path, destination_folder_path)
        # Refresh the file system view
        self.model.setRootPath(self.model.rootPath())

    def create_context_menu(self, position, list_view):
        menu = QtWidgets.QMenu()
        temp = self.model.rootPath()
        if list_view == self.read_write_list_view:
            self.model.setRootPath(self.read_write_model.rootPath())
        selected_index = list_view.indexAt(position)
        if selected_index.isValid():
            # Get the selected item's path
            item_path = self.model.filePath(selected_index)
            if os.path.basename(os.path.dirname(item_path)) == os.path.basename(self.read_write_path) and \
                    list_view == self.read_write_list_view:
                # Disable context menu on users' folders in shares tab
                return
            if os.path.isfile(item_path):
                # Add "Open" action to the context menu
                open_action = menu.addAction("Open")
                open_action.triggered.connect(lambda: open_file(item_path))

            # Add "Rename" action to the context menu
            rename_action = menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self.rename_selected_item(item_path))

            # Add "Delete" action to the context menu
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_selected_item(item_path))

            # Add "Copy" action to the context menu
            copy_action = menu.addAction("Copy")
            copy_action.triggered.connect(lambda: self.copy_item(item_path))

            # Add "Cut" action to the context menu
            cut_action = menu.addAction("Cut")
            cut_action.triggered.connect(lambda: self.cut_item(item_path))

            # Add "Paste" action to the context menu
            paste_action = menu.addAction("Paste")
            paste_action.triggered.connect(lambda: self.paste_item())
        else:
            # Add "Paste" action to the context menu
            paste_action = menu.addAction("Paste")
            paste_action.triggered.connect(lambda: self.paste_item())

            # Add "New" submenu to the context menu
            new_menu = menu.addMenu("New")
            # Add "Create File" action to the "New" submenu
            create_file_action = new_menu.addAction("Create File")
            create_file_action.triggered.connect(self.create_new_file)
            # Add "Create Folder" action to the "New" submenu
            create_folder_action = new_menu.addAction("Create Folder")
            create_folder_action.triggered.connect(self.create_new_directory)
        # Show the context menu at the given position
        menu.exec_(list_view.viewport().mapToGlobal(position))
        self.model.setRootPath(temp)

    def copy_item(self, item_path):
        self.copied_item_path = item_path
        self.cut_item_path = None

    def cut_item(self, item_path):
        self.cut_item_path = item_path
        self.copied_item_path = None

    def paste_item(self):
        destination_path = self.model.rootPath()
        if self.copied_item_path:
            ok = True
            # Copy the file or folder
            if os.path.isfile(self.copied_item_path):
                try:
                    # Copy a file
                    shutil.copy2(self.copied_item_path, destination_path)
                except shutil.SameFileError:
                    ok = False
            elif os.path.isdir(self.copied_item_path):
                try:
                    # Copy a folder
                    shutil.copytree(self.copied_item_path,
                                    os.path.join(destination_path, os.path.basename(self.copied_item_path)))
                except FileExistsError:
                    ok = False
            if ok:
                if FOLDER in self.copied_item_path:
                    rel_copied_item_path = os.path.relpath(self.copied_item_path, DIRECTORY)
                else:
                    rel_copied_item_path = os.path.relpath(self.copied_item_path, self.read_write_path)
                if FOLDER in destination_path:
                    rel_des_item_path = os.path.relpath(destination_path, DIRECTORY)
                else:
                    rel_des_item_path = os.path.relpath(destination_path, self.read_write_path)
                send_data(client_socket, f"copy ||{rel_copied_item_path}||{rel_des_item_path}")
        elif self.cut_item_path:
            try:
                # Move the file or folder
                shutil.move(self.cut_item_path, destination_path)
                if FOLDER in self.cut_item_path:
                    rel_cut_item_path = os.path.relpath(self.cut_item_path, DIRECTORY)
                else:
                    rel_cut_item_path = os.path.relpath(self.cut_item_path, self.read_write_path)
                if FOLDER in destination_path:
                    rel_des_item_path = os.path.relpath(destination_path, DIRECTORY)
                else:
                    rel_des_item_path = os.path.relpath(destination_path, self.read_write_path)
                send_data(client_socket, f"move ||{rel_cut_item_path}||{rel_des_item_path}")
                self.copied_item_path = os.path.join(destination_path, os.path.basename(self.cut_item_path))
                self.cut_item_path = None
            except shutil.Error:
                pass
        # Refresh the file system view
        self.model.setRootPath(self.model.rootPath())

    def delete_selected_item(self, item_path):
        self.model.setRootPath(item_path)
        # Delete the item (file or folder)
        delete_item(item_path)
        # Refresh the file system view
        self.model.setRootPath(self.model.rootPath())
        if FOLDER in item_path:
            relative_path = os.path.relpath(item_path, DIRECTORY)
        else:
            relative_path = os.path.relpath(item_path, self.read_write_path)

        send_data(client_socket, f"delete_item || {relative_path}")

    def rename_selected_item(self, item_path):
        # Open a dialog to get the new name
        self.model.setRootPath(item_path)
        new_name, ok = QInputDialog.getText(self, "Rename Item", "New Name:")
        if ok and new_name:
            if os.path.splitext(new_name)[-1] == '':
                new_name = new_name + os.path.splitext(item_path)[-1]
            # Rename the item
            rename_item(item_path, new_name)
            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())
            if FOLDER in item_path:
                relative_path = os.path.relpath(item_path, DIRECTORY)
            else:
                relative_path = os.path.relpath(item_path, self.read_write_path)
            send_data(client_socket, f"rename_item || {relative_path} || {new_name}")

    def create_new_file(self):
        # Open a dialog to get the new file name
        file_name, ok = QInputDialog.getText(self, "Create New File", "File Name:")
        parent_path = self.model.rootPath()
        if ok and file_name:
            # Check if a directory is selected
            if not os.path.isdir(parent_path):
                parent_path = self.dir_path
            # Construct the path of the new file
            new_file_path = os.path.join(parent_path, file_name)

            # Check if a file or directory with the same name already exists
            if os.path.exists(new_file_path):
                QMessageBox.warning(self, "Error", "A file or directory with the same name already exists.")
                return

            # Create the new file
            with open(new_file_path, 'w'):
                pass  # Do nothing, just create an empty file

            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())
            if FOLDER in new_file_path:
                relative_path = os.path.relpath(new_file_path, DIRECTORY)
            else:
                relative_path = os.path.relpath(new_file_path, self.read_write_path)
            send_data(client_socket, f"create_file || {relative_path}")

    def create_new_directory(self):
        # Open a dialog to get the new directory name
        dir_name, ok = QInputDialog.getText(self, "Create New Directory", "Directory Name:")
        parent_path = self.model.rootPath()
        if ok and dir_name:
            # Check if a directory is selected
            if not os.path.isdir(parent_path):
                parent_path = self.dir_path
            # Construct the path of the new directory
            new_dir_path = os.path.join(parent_path, dir_name)

            # Check if a file or directory with the same name already exists
            if os.path.exists(new_dir_path):
                QMessageBox.warning(self, "Error", "A file or directory with the same name already exists.")
                return

            # Create the new directory
            os.makedirs(new_dir_path)

            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())
            if FOLDER in new_dir_path:
                relative_path = os.path.relpath(new_dir_path, DIRECTORY)
            else:
                relative_path = os.path.relpath(new_dir_path, self.read_write_path)
            send_data(client_socket, f"create_folder || {relative_path}")

    def upload_folders(self, model):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder to Upload",
                                                               QtCore.QDir.homePath())
        parent_path = model.rootPath()
        if directory:
            # Check if a directory is selected
            if not os.path.isdir(parent_path):
                parent_path = self.dir_path
            directory = Directory(directory)
            new_dir = directory.create(os.path.join(parent_path, directory.name))
            # Refresh the file system view
            model.setRootPath(model.rootPath())
            serialized_dir = dumps(new_dir)
            new_dir_path = new_dir.path
            if FOLDER in new_dir_path:
                relative_path = os.path.relpath(new_dir_path, DIRECTORY)
            else:
                relative_path = os.path.relpath(new_dir_path, self.read_write_path)

            # Create a thread and start the network operations
            thread = threading.Thread(target=self.upload_directory, args=(relative_path, serialized_dir,))
            thread.start()

    @staticmethod
    def upload_directory(relative_path, serialized_dir):
        send_data(client_socket, f"upload_dir ||{relative_path}")
        send_data(client_socket, serialized_dir, send_bytes=True)

    def upload_files(self, model):
        file_dialog = QtWidgets.QFileDialog(self, "Select File to Upload")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles | QtWidgets.QFileDialog.Directory)
        file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)  # Show both files and directories
        parent_path = model.rootPath()
        if file_dialog.exec_():
            # Check if a directory is selected
            if not os.path.isdir(parent_path):
                parent_path = self.dir_path
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                # Upload a single file
                file = File(file_path)
                destination_path = os.path.join(parent_path,
                                                file.name)
                shutil.copyfile(file.path, destination_path)
                serialized_file = dumps(file)
                if FOLDER in destination_path:
                    relative_path = os.path.relpath(destination_path, DIRECTORY)
                else:
                    relative_path = os.path.relpath(destination_path, self.read_write_path)

                send_data(client_socket, f"upload_file||{relative_path}")
                send_data(client_socket, serialized_file, send_bytes=True)

            # Refresh the file system view
            model.setRootPath(model.rootPath())


class LoginWindow(QMainWindow, UiLogin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.login_fail_label.hide()
        self.setWindowTitle("Log In")
        disable_keys(self.username_input)
        disable_keys(self.password_input)
        self.login_button.clicked.connect(self.login)

        self.signup_button.clicked.connect(self.goto_signup_screen)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == '' or password == '':
            return
        # perform login logic here
        print(f"Username: {username}")
        print(f"Password: {password}")
        # Send the username and password to the server for signup
        msg = f"login {username} {hashlib.md5(password.encode()).hexdigest()}"
        send_data(client_socket, msg)

        # Receive the server's response
        response = receive_data(client_socket)

        # Check the server's response and show an appropriate message
        if response == "OK":
            # Welcome message
            print(f"Login Successful - Welcome, {username}!")
            send_data(client_socket, "download_folder")
            dir_data = receive_data(client_socket, return_bytes=True)
            folder = loads(dir_data)
            my_folder = folder.create(os.path.join(DIRECTORY, folder.name))

            self.goto_files(my_folder.path)
        elif response == "FAIL":
            print("Login Failed - Invalid username or password")
            self.login_fail_label.show()
        else:
            fail_label = create_fail_label(self, response, QtCore.QRect(150, 260, 285, 18))
            fail_label.show()

    @staticmethod
    def goto_signup_screen():
        widget.addWidget(SignupWindow())
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def goto_files(path):
        widget.addWidget((MainWindow(path)))
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.setFixedWidth(840)
        widget.setFixedHeight(587)


class SignupWindow(QMainWindow, UiSignup):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.confirm_fail_label.hide()
        self.signup_fail_label.hide()
        self.setWindowTitle("Sign Up")
        disable_keys(self.username_input)
        disable_keys(self.password_input)
        disable_keys(self.confirm_password_input)

        self.create_account_button.clicked.connect(self.signup)
        self.back_button.clicked.connect(self.go_back)

    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        if username == '' or password == '' or confirm_password == '':
            return
        if password != confirm_password:
            self.signup_fail_label.hide()
            self.confirm_fail_label.show()
            return
        print("Username:", username)
        print("Password:", password)
        # Create a new socket and connect to the server
        send_data(client_socket, f"signup {username} {hashlib.md5(password.encode()).hexdigest()}")
        # Receive the server's response
        response = receive_data(client_socket)

        # Check the server's response and show an appropriate message
        if response == "OK":
            print(f"Signup Successful - Welcome {username}!")
            path = os.path.join(DIRECTORY, username)
            os.makedirs(path)
            self.goto_files(path)

        else:
            print("Signup Failed - Username already exists")
            self.confirm_fail_label.hide()
            self.signup_fail_label.show()

    @staticmethod
    def go_back():
        widget.setCurrentIndex(widget.currentIndex() - 1)

    @staticmethod
    def goto_files(path):
        widget.addWidget((MainWindow(path)))
        widget.setCurrentIndex(widget.currentIndex() + 1)
        widget.setFixedWidth(840)
        widget.setFixedHeight(587)


if __name__ == "__main__":
    client_socket = None
    try:
        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))
        public_key, private_key = rsa.newkeys(1024)
        public_partner = rsa.PublicKey.load_pkcs1(client_socket.recv(1024))
        client_socket.send(public_key.save_pkcs1("PEM"))
        # Receive the encrypted symmetric key from the server
        encrypted_symmetric_key = client_socket.recv(1024)
        # Decrypt the symmetric key using the client's private key
        symmetric_key = rsa.decrypt(encrypted_symmetric_key, private_key)
        # Create a Fernet instance with the symmetric key
        fernet = Fernet(symmetric_key)
        app = QApplication(sys.argv)
        widget = QtWidgets.QStackedWidget()
        widget.addWidget(LoginWindow())
        widget.setFixedHeight(600)
        widget.setFixedWidth(460)
        widget.show()

        sys.exit(app.exec_())
    except ConnectionRefusedError:
        print("Server is closed")
    finally:
        if client_socket:
            client_socket.close()
