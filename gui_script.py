import hashlib
import socket

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, \
    QHBoxLayout, QListWidget, QStatusBar, QMenuBar, QDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys

from PyQt5.uic import loadUi

SERVER_IP = '127.0.0.1'  # '10.100.102.14'
PORT = 8080


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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("FileSpace")
        self.resize(460, 600)
        self.setMouseTracking(True)
        self.setTabletTracking(True)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        title_label = QLabel(central_widget)
        title_label.setGeometry(QtCore.QRect(134, 60, 191, 51))
        title_label.setText("FileSpace")
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        title_label.setFont(font)

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
        disable_key(self.username_input, Qt.Key_Space)

        self.password_input = QLineEdit(central_widget)
        self.password_input.setGeometry(QtCore.QRect(180, 210, 230, 31))
        self.password_input.setEchoMode(QLineEdit.Password)
        disable_key(self.password_input, Qt.Key_Space)

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
        signup_button.clicked.connect(self.goto_signup_screen)

        self.login_fail_label = create_fail_label(central_widget, "Login Failed - Invalid username or password",
                                                  (85, 260, 285, 18))

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

            # Show the download and upload buttons
        else:
            print("Login Failed - Invalid username or password")
            self.login_fail_label.show()

    @staticmethod
    def goto_signup_screen():
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

        title_label = QLabel(central_widget)
        title_label.setGeometry(QtCore.QRect(134, 60, 191, 51))
        title_label.setText("FileSpace")
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        title_label.setFont(font)

        username_label = QLabel(central_widget)
        username_label.setGeometry(QtCore.QRect(50, 150, 101, 23))
        username_label.setText("Username")
        font = QtGui.QFont()
        font.setPointSize(16)
        username_label.setFont(font)

        self.username_input = QLineEdit(central_widget)
        self.username_input.setGeometry(QtCore.QRect(180, 150, 230, 31))
        disable_key(self.username_input, Qt.Key_Space)

        password_label = QLabel(central_widget)
        password_label.setGeometry(QtCore.QRect(20, 210, 161, 31))
        password_label.setText("Create Password")
        font = QtGui.QFont()
        font.setPointSize(16)
        password_label.setFont(font)

        self.password_input = QLineEdit(central_widget)
        self.password_input.setGeometry(QtCore.QRect(209, 210, 201, 31))
        self.password_input.setEchoMode(QLineEdit.Password)
        disable_key(self.password_input, Qt.Key_Space)

        confirm_password_label = QLabel(central_widget)
        confirm_password_label.setGeometry(QtCore.QRect(20, 270, 171, 31))
        confirm_password_label.setText("Confirm Password")
        font = QtGui.QFont()
        font.setPointSize(16)
        confirm_password_label.setFont(font)

        self.confirm_password_input = QLineEdit(central_widget)
        self.confirm_password_input.setGeometry(QtCore.QRect(209, 270, 201, 31))
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        disable_key(self.confirm_password_input, Qt.Key_Space)

        create_account_button = QPushButton(central_widget)
        create_account_button.setGeometry(QtCore.QRect(150, 350, 151, 35))
        font = QtGui.QFont()
        font.setPointSize(16)
        create_account_button.setFont(font)
        create_account_button.setText("Create Account")

        back_button = QPushButton(central_widget)
        back_button.setGeometry(QtCore.QRect(0, 0, 75, 23))
        back_button.setText("Back")

        self.signup_fail_label = create_fail_label(central_widget, "Signup Failed - Username already exists",
                                                   (95, 320, 285, 18))
        self.confirm_fail_label = create_fail_label(central_widget, "Signup Failed - Couldn't confirm password",
                                                    (95, 320, 285, 18))

        create_account_button.clicked.connect(self.signup)
        back_button.clicked.connect(self.goto_mainwindow)

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

        else:
            print("Signup Failed - Username already exists")
            self.confirm_fail_label.hide()
            self.signup_fail_label.show()

    @staticmethod
    def goto_mainwindow():
        main_win = MainWindow()
        widget.addWidget(main_win)
        widget.setCurrentIndex(widget.currentIndex() + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    main_window = MainWindow()
    widget.addWidget(main_window)
    widget.setFixedHeight(600)
    widget.setFixedWidth(460)
    widget.show()
    sys.exit(app.exec_())
