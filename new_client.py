import hashlib
import os
import socket
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, \
    QHBoxLayout, QListWidget

# Define the server host and port
SERVER_IP = '127.0.0.1'  # '10.100.102.14'
PORT = 8080


class SyncWindow(QWidget):
    def __init__(self, local_path, remote_path, sftp):
        super().__init__()
        self.setWindowTitle("Sync")
        self.setGeometry(100, 100, 300, 150)

        self.local_path = local_path
        self.remote_path = remote_path
        self.sftp = sftp

        self.file_list = QListWidget()
        self.update_file_list()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Synced files:"))
        layout.addWidget(self.file_list)
        self.setLayout(layout)

    def update_file_list(self):
        files = self.sftp.listdir(self.remote_path)
        self.file_list.clear()
        for file in files:
            self.file_list.addItem(file)

    def sync_files(self):
        # synchronize local folder with remote folder
        os.system(f"rsync -avz {self.local_path} {self.remote_path}")
        self.update_file_list()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # perform login logic here
        print("Username:", username)
        print("Password:", password)
        if username == '' or password == '':
            return
        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))
        # Send the username and password to the server for verification
        client_socket.send(f"login {username} {hashlib.md5(password.encode()).hexdigest()}".encode())

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Check the server's response and show an appropriate message
        if response == "OK":
            # Welcome message
            print("Login Successful", f"Welcome, {username}!")

            # Show the download and upload buttons
        else:
            print("Login Failed", "Invalid username or password")


"""            self.sync_window = SyncWindow("/local/folder", "/remote/folder", sftp)
            self.sync_window.show()"""


class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signup")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        signup_button = QPushButton("Signup")
        signup_button.clicked.connect(self.signup)

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(signup_button)

        self.setLayout(layout)

    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # perform signup logic here
        print("Username:", username)
        print("Password:", password)
        if username == '' or password == '':
            return
        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the username and password to the server for signup
        client_socket.send(f"signup {username} {hashlib.md5(password.encode()).hexdigest()}".encode())

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Check the server's response and show an appropriate message
        if response == "OK":
            print("Signup Successful", f"Welcome, {username}!")

        else:
            print("Signup Failed", "Username already exists")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login/Signup")
        self.setGeometry(100, 100, 300, 150)

        self.login_window = LoginWindow()
        self.signup_window = SignupWindow()

        central_widget = QWidget()
        layout = QHBoxLayout()

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.show_login)

        signup_button = QPushButton("Signup")
        signup_button.clicked.connect(self.show_signup)

        layout.addWidget(login_button)
        layout.addWidget(signup_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_login(self):
        self.login_window.show()

    def show_signup(self):
        self.signup_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
