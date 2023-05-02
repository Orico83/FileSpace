import hashlib
import socket

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, \
    QHBoxLayout, QListWidget, QStatusBar, QMenuBar, QDialog
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from PyQt5.uic import loadUi

SERVER_IP = '127.0.0.1'  # '10.100.102.14'
PORT = 8080


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("FileSpace")
        self.resize(460, 600)
        self.setMouseTracking(True)
        self.setTabletTracking(True)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel(central_widget)
        label.setGeometry(QtCore.QRect(134, 60, 191, 51))
        label.setText("FileSpace")
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)

        username_label = QLabel(central_widget)
        username_label.setGeometry(QtCore.QRect(50, 150, 101, 23))
        username_label.setText("Username")
        font = QtGui.QFont()
        font.setPointSize(16)
        username_label.setFont(font)

        password_label = QLabel(central_widget)
        password_label.setGeometry(QtCore.QRect(50, 210, 101, 31))
        password_label.setText("Password")
        font = QtGui.QFont()
        font.setPointSize(16)
        password_label.setFont(font)

        self.username_input = QLineEdit(central_widget)
        self.username_input.setGeometry(QtCore.QRect(180, 150, 230, 31))

        self.password_input = QLineEdit(central_widget)
        self.password_input.setGeometry(QtCore.QRect(180, 210, 230, 31))
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton(central_widget)
        login_button.setGeometry(QtCore.QRect(180, 290, 100, 35))
        login_button.setText("Log In")
        font = QtGui.QFont()
        font.setPointSize(16)
        login_button.setFont(font)
        login_button.clicked.connect(self.login)

        create_account_label = QLabel(central_widget)
        create_account_label.setGeometry(QtCore.QRect(50, 350, 171, 30))
        create_account_label.setText("Don\'t have an account?")
        font = QtGui.QFont()
        font.setPointSize(12)
        create_account_label.setFont(font)

        signup_button = QPushButton(central_widget)
        signup_button.setGeometry(QtCore.QRect(220, 350, 100, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        signup_button.setFont(font)
        signup_button.setStyleSheet("color: rgb(0, 0, 255)")
        signup_button.setFlat(True)
        signup_button.setText("Sign Up")
        signup_button.clicked.connect(self.signup_screen)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 460, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == '' or password == '':
            return
        # perform login logic here
        print("Username:", username)
        print("Password:", password)
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
            print("Login Successful - Welcome, {username}!")

            # Show the download and upload buttons
        else:
            print("Login Failed - Invalid username or password")
            login_fail_label = QLabel(self.central_widget)
            login_fail_label.setGeometry(QtCore.QRect(90, 260, 285, 18))
            login_fail_label.setText("Login Failed - Invalid username or password")
            font = QtGui.QFont()
            font.setPointSize(11)
            login_fail_label.setFont(font)
            login_fail_label.setStyleSheet("color: rgb(255, 0, 0)")

    def signup_screen(self):
        signup = SignUpScreen()
        widget.addWidget(signup)
        widget.setCurrentIndex(widget.currentIndex() + 1)



class SignUpScreen(QMainWindow):
    def __init__(self):
        super(SignUpScreen, self).__init__()
        self.setWindowTitle("FileSpace")
        self.resize(460, 600)
        self.setMouseTracking(True)
        self.setTabletTracking(True)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        label = QLabel(central_widget)
        label.setGeometry(QtCore.QRect(134, 60, 191, 51))
        label.setText("FileSpace")
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)

        username_label = QLabel(central_widget)
        username_label.setGeometry(QtCore.QRect(50, 150, 101, 23))
        username_label.setText("Username")
        font = QtGui.QFont()
        font.setPointSize(16)
        username_label.setFont(font)

        self.username_input = QLineEdit(central_widget)
        self.username_input.setGeometry(QtCore.QRect(180, 150, 230, 31))

        password_label = QLabel(central_widget)
        password_label.setGeometry(QtCore.QRect(20, 210, 161, 31))
        password_label.setText("Create Password")
        font = QtGui.QFont()
        font.setPointSize(16)
        password_label.setFont(font)

        self.password_input = QLineEdit(central_widget)
        self.password_input.setGeometry(QtCore.QRect(209, 210, 201, 31))
        self.password_input.setEchoMode(QLineEdit.Password)
# TODO fix confirm password problem
        confirm_password_label = QLabel(central_widget)
        confirm_password_label.setGeometry(QtCore.QRect(20, 270, 171, 31))
        password_label.setText("Confirm Password")
        font = QtGui.QFont()
        font.setPointSize(16)
        confirm_password_label.setFont(font)

        self.confirm_password_input = QLineEdit(central_widget)
        self.confirm_password_input.setGeometry(QtCore.QRect(209, 270, 201, 31))
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        signup_button = QtWidgets.QPushButton(central_widget)
        signup_button.setGeometry(QtCore.QRect(150, 350, 151, 35))
        font = QtGui.QFont()
        font.setPointSize(16)
        signup_button.setFont(font)
        signup_button.setText("Create Account")

        signup_button.clicked.connect(self.signup)

    def signup(self):
        username = self.username_input.text()
        if self.password_input.text() == self.confirm_password.text():
            password = self.password_input.text()
            if username == '' or password == '':
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
                # Close the client socket
                client_socket.close()

            # Check the server's response and show an appropriate message
            if response == "OK":
                print("Signup Successful - Welcome {username}!")

            else:
                print("Signup Failed - Username already exists")
        else:
            print("Signup Failed - ")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    main_window = MainWindow()
    widget.addWidget(main_window)
    widget.setFixedHeight(600)
    widget.setFixedWidth(460)
    widget.show()
    sys.exit(app.exec_())
