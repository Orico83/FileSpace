


from PyQt5 import QtCore, QtGui, QtWidgets


class UiLogin(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(460, 600)
        MainWindow.setMouseTracking(True)
        MainWindow.setTabletTracking(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title_label = QtWidgets.QLabel(self.centralwidget)
        self.title_label.setGeometry(QtCore.QRect(134, 60, 191, 51))
        font = QtGui.QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setMouseTracking(False)
        self.title_label.setObjectName("title_label")
        self.username_label = QtWidgets.QLabel(self.centralwidget)
        self.username_label.setGeometry(QtCore.QRect(50, 150, 101, 23))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.username_label.setFont(font)
        self.username_label.setObjectName("username_label")
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setGeometry(QtCore.QRect(50, 210, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.username_input = QtWidgets.QLineEdit(self.centralwidget)
        self.username_input.setGeometry(QtCore.QRect(180, 150, 230, 31))
        self.username_input.setObjectName("username_input")
        self.password_input = QtWidgets.QLineEdit(self.centralwidget)
        self.password_input.setGeometry(QtCore.QRect(180, 210, 230, 31))
        self.password_input.setTabletTracking(False)
        self.password_input.setAutoFillBackground(False)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setClearButtonEnabled(False)
        self.password_input.setObjectName("password_input")
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setGeometry(QtCore.QRect(180, 290, 100, 35))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.login_button.setFont(font)
        self.login_button.setObjectName("login_button")
        self.create_account_label = QtWidgets.QLabel(self.centralwidget)
        self.create_account_label.setGeometry(QtCore.QRect(50, 350, 171, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.create_account_label.setFont(font)
        self.create_account_label.setObjectName("create_account_label")
        self.signup_button = QtWidgets.QPushButton(self.centralwidget)
        self.signup_button.setGeometry(QtCore.QRect(220, 350, 100, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.signup_button.setFont(font)
        self.signup_button.setStyleSheet("color: rgb(0, 0, 255)")
        self.signup_button.setFlat(True)
        self.signup_button.setObjectName("signup_button")
        self.login_fail_label = QtWidgets.QLabel(self.centralwidget)
        self.login_fail_label.setEnabled(True)
        self.login_fail_label.setGeometry(QtCore.QRect(85, 260, 285, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.login_fail_label.setFont(font)
        self.login_fail_label.setStyleSheet("color:rgb(255, 0, 0)")
        self.login_fail_label.setObjectName("login_fail_label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title_label.setText(_translate("MainWindow", "FileSpace"))
        self.username_label.setText(_translate("MainWindow", "Username"))
        self.password_label.setText(_translate("MainWindow", "Password"))
        self.login_button.setText(_translate("MainWindow", "Log In"))
        self.create_account_label.setText(_translate("MainWindow", "Don\'t have an account?"))
        self.signup_button.setText(_translate("MainWindow", "Sign Up"))
        self.login_fail_label.setText(_translate("MainWindow", "Login Failed - Invalid username or password"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiLogin()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
