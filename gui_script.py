import hashlib
import os
import shutil
import socket
import threading
import time
from pickle import loads, dumps
import rsa
from cryptography.fernet import Fernet
from login_window import UiLogin
from signup_window import UiSignup
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QFileSystemModel, QInputDialog, QMessageBox, \
    QPushButton
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QFileSystemWatcher
import sys
from file_classes import File, Directory
from main_window import Ui_MainWindow

SERVER_IP = '127.0.0.1'
PORT = 8080
FOLDER = r"C:\Users\orico\Desktop\FS"
CHUNK_SIZE = 4096
KEYS_TO_DISABLE = [Qt.Key_Space, Qt.Key_Period, Qt.Key_Slash, Qt.Key_Comma, Qt.Key_Semicolon, Qt.Key_Colon, Qt.Key_Bar,
                   Qt.Key_Backslash, Qt.Key_BracketLeft, Qt.Key_BracketRight, Qt.Key_ParenLeft, Qt.Key_ParenRight,
                   Qt.Key_BraceLeft, Qt.Key_BraceRight, Qt.Key_Apostrophe, Qt.Key_QuoteDbl]
REFRESH_FREQUENCY = 5
NO_FRIENDS = "No Friends Added"
NO_FRIEND_REQUESTS = "No Friend Requests"



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


"""def create_fail_label(parent, text, geometry):
    fail_label = QtWidgets.QLabel(parent)
    fail_label.setGeometry(QtCore.QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
    fail_label.setText(text)
    fail_label.hide()
    font = QtGui.QFont()
    font.setPointSize(11)
    fail_label.setFont(font)
    fail_label.setStyleSheet("color: rgb(255, 0, 0)")
    return fail_label"""


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
        self.directory_history = []  # List to store directory history
        self.users = []
        self.friends = []
        self.friend_requests = []
        self.sent_requests = []
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
        # self.refresh_users()
        self.list_view.doubleClicked.connect(self.on_list_view_double_clicked)
        self.upload_files_button.clicked.connect(self.upload_files)  # Connect the upload button to the method
        self.upload_folders_button.clicked.connect(self.upload_folders)

        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.create_context_menu)
        self.go_back_button.hide()
        self.go_back_button.clicked.connect(self.go_back)

        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.dir_path)
        self.file_timestamps = {}
        self.recursively_add_paths(self.dir_path)  # Add subdirectories recursively
        self.watcher.fileChanged.connect(self.file_changed)
        # self.initiate_friends()
        self.friends_list_widget.itemDoubleClicked.connect(self.friend_double_clicked)
        self.friend_requests_list_widget.itemDoubleClicked.connect(self.friend_request_double_clicked)

        self.search_bar.textChanged.connect(self.search_users)
        self.search_results_list.itemDoubleClicked.connect(self.user_double_clicked)
        refreshes_thread = threading.Thread(target=self.handle_refreshes)
        refreshes_thread.start()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Perform any necessary cleanup or save operations here
            event.accept()
        else:
            event.ignore()

    def send_message(self, message):
        with self.lock:
            client_socket.send(fernet.encrypt(message))

    def handle_refreshes(self):
        while not self.exit:
            threading.Thread(target=self.refresh).start()
            time.sleep(REFRESH_FREQUENCY)

    def refresh(self):
        try:
            with self.lock:
                client_socket.send(fernet.encrypt("refresh".encode()))
                data = fernet.decrypt(client_socket.recv(1024)).decode()
                self.users = data.split('||')[0].split(',')
                print(self.users)
                self.users.remove(os.path.basename(self.dir_path))
                friends = data.split('||')[1].split(',')
                friend_requests = data.split('||')[2].split(',')
                self.friends = friends if friends[0] else []
                self.friend_requests = friend_requests if friend_requests[0] else []
                self.friends_list_widget.clear()
                # TODO delete the 2 lines below
                print(self.friends)
                print(self.friend_requests)
                if not self.friends:
                    self.friends_list_widget.addItem(NO_FRIENDS)
                else:
                    self.friends_list_widget.addItems(self.friends)
                self.friend_requests_list_widget.clear()
                if not self.friend_requests:
                    self.friend_requests_list_widget.addItem(NO_FRIEND_REQUESTS)
                else:
                    self.friend_requests_list_widget.addItems(self.friend_requests)

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
            # TODO: Implement logic for sharing read-only permissions
            client_socket.send(fernet.encrypt(f"share||{friend_name}||read only".encode()))
        elif clicked_button == 1:
            print(f"Sharing read-write with friend: {friend_name}")
            # TODO: Implement logic for sharing read-write permissions
            client_socket.send(fernet.encrypt(f"share||{friend_name}||read write".encode()))

        else:
            print("Share canceled")

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
        client_socket.send(fernet.encrypt(f"remove_friend ||{friend_name}".encode()))

    def send_friend_request(self, user):
        if user not in self.friends:
            self.sent_requests.append(user)
            client_socket.send(fernet.encrypt(f"send_friend_request ||{user}".encode()))
            print(f"Sent a friend request to {user}")
            response = fernet.decrypt(client_socket.recv(1024)).decode()
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
        client_socket.send(fernet.encrypt(f"add_friend {user}".encode()))
        client_socket.recv(1024)
        print(f"added {user}")

    def remove_friend_request(self, user):
        self.friend_requests.remove(user)
        if self.friend_requests:
            index = self.friend_requests_list_widget.currentRow()
            self.friend_requests_list_widget.takeItem(index)
        else:
            self.friend_requests_list_widget.clear()
            self.friend_requests_list_widget.addItem(NO_FRIEND_REQUESTS)
        client_socket.send(fernet.encrypt(f"remove_friend_request ||{user}".encode()))

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
            client_socket.send(fernet.encrypt(f"file_edit ||{os.path.relpath(path, FOLDER)}||{file_size}".encode()))
            client_socket.recv(1024)  # Wait for the server's acknowledgement
            client_socket.send(fernet.encrypt(file_data))
            client_socket.recv(1024)  # Wait for the server's acknowledgement

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

    def update_directory_history(self, directory_path):
        # Add the current directory path to the history
        self.directory_history.append(directory_path)

    def set_initial_directory(self):
        self.model.setRootPath(self.dir_path)
        self.list_view.setRootIndex(self.model.index(self.dir_path))
        self.directory_history.append(self.dir_path)
        self.go_back_button.hide()

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

    def create_context_menu(self, position):
        menu = QtWidgets.QMenu()
        selected_index = self.list_view.indexAt(position)
        if selected_index.isValid():
            # Get the selected item's path
            item_path = self.model.filePath(selected_index)
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
        menu.exec_(self.list_view.viewport().mapToGlobal(position))

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
                client_socket.send(fernet.encrypt(f"copy ||{os.path.relpath(self.copied_item_path, FOLDER)}||"
                                                  f"{os.path.relpath(destination_path, FOLDER)}".encode()))
        elif self.cut_item_path:
            try:
                # Move the file or folder
                shutil.move(self.cut_item_path, destination_path)
                client_socket.send(fernet.encrypt(f"move ||{os.path.relpath(self.cut_item_path, FOLDER)}||"
                                                  f"{os.path.relpath(destination_path, FOLDER)}".encode()))
                self.copied_item_path = os.path.join(destination_path, os.path.basename(self.cut_item_path))
                self.cut_item_path = None
            except shutil.Error:
                pass
        # Refresh the file system view
        self.model.setRootPath(self.model.rootPath())

    def delete_selected_item(self, item_path):
        # Delete the item (file or folder)
        delete_item(item_path)
        # Refresh the file system view
        self.model.setRootPath(self.model.rootPath())
        relative_path = os.path.relpath(item_path, FOLDER)

        client_socket.send(fernet.encrypt(f"delete_item || {relative_path}".encode()))

    def rename_selected_item(self, item_path):
        # Open a dialog to get the new name
        new_name, ok = QInputDialog.getText(self, "Rename Item", "New Name:")
        if ok and new_name:
            if os.path.splitext(new_name)[-1] == '':
                new_name = new_name + os.path.splitext(item_path)[-1]
            # Rename the item
            rename_item(item_path, new_name)
            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())
            relative_path = os.path.relpath(item_path, FOLDER)
            client_socket.send(fernet.encrypt(f"rename_item || {relative_path} || {new_name}".encode()))

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
            relative_path = os.path.relpath(new_file_path, FOLDER)
            client_socket.send(fernet.encrypt(f"create_file || {relative_path}".encode()))

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
            relative_path = os.path.relpath(new_dir_path, FOLDER)
            client_socket.send(fernet.encrypt(f"create_folder || {relative_path}".encode()))

    def upload_folders(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder to Upload",
                                                               QtCore.QDir.homePath())
        parent_path = self.model.rootPath()
        if directory:
            # Check if a directory is selected
            if not os.path.isdir(parent_path):
                parent_path = self.dir_path
            directory = Directory(directory)
            new_dir = directory.create(os.path.join(parent_path, directory.name))
            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())
            serialized_dir = dumps(new_dir)
            encrypted_dir = fernet.encrypt(serialized_dir)

            def upload_directory():
                encrypted_message = fernet.encrypt(
                    f"upload_dir || {len(encrypted_dir)} || {os.path.relpath(new_dir.path, FOLDER)}".encode())
                client_socket.send(encrypted_message)
                client_socket.recv(1024)
                client_socket.send(encrypted_dir)
                client_socket.recv(2)

            # Create a thread and start the network operations
            thread = threading.Thread(target=upload_directory)
            thread.start()

    def upload_files(self):
        file_dialog = QtWidgets.QFileDialog(self, "Select File to Upload")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles | QtWidgets.QFileDialog.Directory)
        file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)  # Show both files and directories
        parent_path = self.model.rootPath()
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
                encrypted_file = fernet.encrypt(serialized_file)

                client_socket.send(fernet.encrypt(f"upload_file || {len(encrypted_file)} ||"
                                                  f" {os.path.relpath(destination_path, FOLDER)}".encode()))
                client_socket.recv(1024)
                client_socket.send(encrypted_file)
                client_socket.recv(1024)

            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())


class LoginWindow(QMainWindow, UiLogin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        client_socket.send(fernet.encrypt(f"login {username} {hashlib.md5(password.encode()).hexdigest()}".encode()))

        # Receive the server's response
        response = fernet.decrypt(client_socket.recv(1024)).decode().strip()

        # Check the server's response and show an appropriate message
        if response == "OK":
            # Welcome message
            print(f"Login Successful - Welcome, {username}!")
            client_socket.send(fernet.encrypt("download_folder".encode()))
            data = fernet.decrypt(client_socket.recv(1024)).decode()
            data_len = int(data.split(":")[1])
            client_socket.send(fernet.encrypt("OK".encode()))
            # Receive the directory data
            bytes_received = 0
            encrypted_dir_data = b''
            while bytes_received < data_len:
                chunk = client_socket.recv(CHUNK_SIZE)
                bytes_received += len(chunk)
                encrypted_dir_data += chunk

            # Decrypt the directory data
            dir_data = fernet.decrypt(encrypted_dir_data)
            folder = loads(dir_data)
            f = folder.create(os.path.join(FOLDER, folder.name))
            self.goto_files(f.path)
        else:
            print("Login Failed - Invalid username or password")
            self.login_fail_label.show()

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        client_socket.send(fernet.encrypt(f"signup {username} {hashlib.md5(password.encode()).hexdigest()}".encode()))
        # Receive the server's response
        response = fernet.decrypt(client_socket.recv(1024)).decode().strip()

        # Check the server's response and show an appropriate message
        if response == "OK":
            print(f"Signup Successful - Welcome {username}!")
            path = os.path.join(FOLDER, username)
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
