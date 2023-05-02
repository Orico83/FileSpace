# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SignupScreen.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QMainWindow, QLineEdit


class SignUpScreen(QMainWindow):
    def __init__(self):
        super().__init__()
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
        password_label.setGeometry(QtCore.QRect(20, 210, 161, 31))
        password_label.setText("Create Password")
        font = QtGui.QFont()
        font.setPointSize(16)
        password_label.setFont(font)

        self.username_input = QLineEdit(central_widget)
        self.username_input.setGeometry(QtCore.QRect(180, 150, 230, 31))

        self.password_input = QLineEdit(central_widget)
        self.password_input.setGeometry(QtCore.QRect(209, 210, 230, 31))
        self.password_input.setEchoMode(QLineEdit.Password)

        confirm_password_label = QLabel(central_widget)
        confirm_password_label.setGeometry(QtCore.QRect(20, 270, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        confirm_password_label.setFont(font)
        password_label.setText("Confirm Password")

        self.password_input_2 = QLineEdit(central_widget)
        self.password_input_2.setGeometry(QtCore.QRect(209, 270, 201, 31))
        self.password_input_2.setEchoMode(QtWidgets.QLineEdit.Password)

        signup_button = QtWidgets.QPushButton(central_widget)
        signup_button.setGeometry(QtCore.QRect(150, 350, 151, 35))
        font = QtGui.QFont()
        font.setPointSize(16)
        signup_button.setFont(font)
        signup_button.setText("Create Account")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
