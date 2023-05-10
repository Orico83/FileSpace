import hashlib
import os
import shutil
import socket
from pickle import loads

from login_window import UiLogin
from signup_window import UiSignup
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QFileSystemModel, QTreeView, QVBoxLayout, \
    QInputDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys
from file_classes import File, Directory
from main_window import Ui_MainWindow

SERVER_IP = '127.0.0.1'
PORT = 8080
FOLDER = r'C:\Users\orico\OneDrive\שולחן העבודה\FS'


def disable_key(field, key):
    field.keyPressEvent = lambda event: event.ignore() if event.key() == key else QLineEdit.keyPressEvent(
        field, event)


# Example function to open a file
def open_file(file_path):
    # Open the file using the default system application
    os.startfile(file_path)


# Example function to delete a file or folder
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
    fail_label.setGeometry(QtCore.QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
    fail_label.setText(text)
    fail_label.hide()
    font = QtGui.QFont()
    font.setPointSize(11)
    fail_label.setFont(font)
    fail_label.setStyleSheet("color: rgb(255, 0, 0)")
    return fail_label


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self, dir_path):
        super().__init__()
        self.dir_path = dir_path
        self.setupUi(self)
        self.model = QFileSystemModel()
        self.model.setRootPath(dir_path)
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(dir_path))
        self.tree_view.setAlternatingRowColors(True)
        self.upload_files_button.clicked.connect(self.upload_files)  # Connect the upload button to the method
        self.upload_folders_button.clicked.connect(self.upload_folders)

        # Connect the buttons for file and folder actions
        self.open_button.clicked.connect(self.open_selected_item)
        self.delete_button.clicked.connect(self.delete_selected_item)
        self.rename_button.clicked.connect(self.rename_selected_item)

        self.create_folder_button.clicked.connect(self.create_new_directory)
        self.create_file_button.clicked.connect(self.create_new_file)

    def open_selected_item(self):
        # Get the selected item's path
        selected_index = self.tree_view.currentIndex()
        item_path = self.model.filePath(selected_index)

        # Open the item (assuming it's a file)
        if os.path.isfile(item_path):
            open_file(item_path)

    def delete_selected_item(self):
        # Get the selected item's path
        selected_index = self.tree_view.currentIndex()
        item_path = self.model.filePath(selected_index)

        # Delete the item (file or folder)
        delete_item(item_path)

        # Refresh the file system view
        self.model.setRootPath(self.model.rootPath())

    def rename_selected_item(self):
        # Get the selected item's path
        selected_index = self.tree_view.currentIndex()
        item_path = self.model.filePath(selected_index)

        # Open a dialog to get the new name
        new_name, ok = QInputDialog.getText(self, "Rename Item", "New Name:")
        if ok and new_name:
            # Rename the item
            rename_item(item_path, new_name)

            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())

    def create_new_file(self):
        # Open a dialog to get the new file name
        file_name, ok = QInputDialog.getText(self, "Create New File", "File Name:")
        parent_index = self.tree_view.currentIndex()
        parent_path = self.model.filePath(parent_index)
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
            with open(new_file_path, 'w') as file:
                pass  # Do nothing, just create an empty file

            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())

    def create_new_directory(self):
        # Open a dialog to get the new directory name
        dir_name, ok = QInputDialog.getText(self, "Create New Directory", "Directory Name:")
        parent_index = self.tree_view.currentIndex()
        parent_path = self.model.filePath(parent_index)
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

    def upload_folders(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder to Upload", QtCore.QDir.homePath())
        if directory:
            directory = Directory(directory)
            directory.create(self.dir_path)
            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())

    def upload_files(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles | QtWidgets.QFileDialog.Directory)
        file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)  # Show both files and directories
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                if os.path.isfile(file_path):
                    # Upload a single file
                    file = File(file_path)
                    destination_path = os.path.join(self.dir_path,
                                                    file.name)
                    shutil.copyfile(file.path, destination_path)
                elif os.path.isdir(file_path):
                    # Upload a directory
                    directory = Directory(file_path)
                    destination_path = os.path.join(FOLDER, self.model.filePath(self.tree_view.currentIndex()),
                                                    directory.name)
                    directory.create(destination_path)

            # Refresh the file system view
            self.model.setRootPath(self.model.rootPath())


class LoginWindow(QMainWindow, UiLogin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.login_fail_label.hide()

        disable_key(self.username_input, Qt.Key_Space)
        disable_key(self.password_input, Qt.Key_Space)
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
        # Create a new socket and connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, PORT))
            # Send the username and password to the server for signup
            client_socket.send(f"login {username} {hashlib.md5(password.encode()).hexdigest()}".encode())
            # Receive the server's response
            response = client_socket.recv(1024).decode().strip()

            # Check the server's response and show an appropriate message
            if response == "OK":
                # Welcome message
                print(f"Login Successful - Welcome, {username}!")
                client_socket.send("download_folder".encode())
                folder: Directory = loads(client_socket.recv(1024))
                f = folder.create(FOLDER)
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

        disable_key(self.username_input, Qt.Key_Space)
        disable_key(self.password_input, Qt.Key_Space)
        disable_key(self.confirm_password_input, Qt.Key_Space)

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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, PORT))
            # Send the username and password to the server for signup
            client_socket.send(f"signup {username} {hashlib.md5(password.encode()).hexdigest()}".encode())
            # Receive the server's response
            response = client_socket.recv(1024).decode().strip()

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
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(LoginWindow())
    widget.setFixedHeight(600)
    widget.setFixedWidth(460)
    widget.show()
    sys.exit(app.exec_())
