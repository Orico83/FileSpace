import hashlib
import os
import socket
from pickle import loads

from login_window import UiLogin
from signup_window import UiSignup
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QFileSystemModel, QTreeView, QVBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys
from file_classes import File, Directory

SERVER_IP = '127.0.0.1'
PORT = 8080
FOLDER = 'D:'


def disable_key(field, key):
    field.keyPressEvent = lambda event: event.ignore() if event.key() == key else QLineEdit.keyPressEvent(
        field, event)


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


class FileSystemView(QWidget):
    def __init__(self, dir_path):
        super().__init__()
        appWidth = 800
        appHeight = 300
        self.setWindowTitle('File System Viewer')
        self.setGeometry(300, 300, appWidth, appHeight)

        self.model = QFileSystemModel()
        self.model.setRootPath(dir_path)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(dir_path))
        self.tree.setColumnWidth(0, 250)
        self.tree.setAlternatingRowColors(True)

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)


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
                folder.create(FOLDER)
                self.goto_files(folder.path)
                # Show the download and upload buttons
            else:
                print("Login Failed - Invalid username or password")
                self.login_fail_label.show()

    @staticmethod
    def goto_signup_screen():
        widget.addWidget(SignupWindow())
        widget.setCurrentIndex(widget.currentIndex() + 1)

    @staticmethod
    def goto_files(path):
        widget.addWidget((FileSystemView(path)))
        widget.setCurrentIndex(widget.currentIndex() + 1)


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
        widget.addWidget((FileSystemView(path)))
        widget.setCurrentIndex(widget.currentIndex() + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(LoginWindow())
    widget.setFixedHeight(600)
    widget.setFixedWidth(460)
    widget.show()
    sys.exit(app.exec_())
