


from PyQt5 import QtCore, QtGui, QtWidgets


class UiSignup(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(460, 600)
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
        self.username_input = QtWidgets.QLineEdit(self.centralwidget)
        self.username_input.setGeometry(QtCore.QRect(180, 150, 230, 31))
        self.username_input.setObjectName("username_input")
        self.password_input = QtWidgets.QLineEdit(self.centralwidget)
        self.password_input.setGeometry(QtCore.QRect(209, 210, 201, 31))
        self.password_input.setTabletTracking(False)
        self.password_input.setAutoFillBackground(False)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setClearButtonEnabled(False)
        self.password_input.setObjectName("password_input")
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setGeometry(QtCore.QRect(20, 210, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.confirm_password_label = QtWidgets.QLabel(self.centralwidget)
        self.confirm_password_label.setGeometry(QtCore.QRect(20, 270, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.confirm_password_label.setFont(font)
        self.confirm_password_label.setObjectName("confirm_password_label")
        self.confirm_password_input = QtWidgets.QLineEdit(self.centralwidget)
        self.confirm_password_input.setGeometry(QtCore.QRect(209, 270, 201, 31))
        self.confirm_password_input.setTabletTracking(False)
        self.confirm_password_input.setAutoFillBackground(False)
        self.confirm_password_input.setText("")
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_input.setClearButtonEnabled(False)
        self.confirm_password_input.setObjectName("confirm_password_input")
        self.create_account_button = QtWidgets.QPushButton(self.centralwidget)
        self.create_account_button.setGeometry(QtCore.QRect(150, 350, 151, 35))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.create_account_button.setFont(font)
        self.create_account_button.setObjectName("create_account_button")
        self.back_button = QtWidgets.QPushButton(self.centralwidget)
        self.back_button.setGeometry(QtCore.QRect(0, 0, 75, 23))
        self.back_button.setObjectName("pushButton")
        self.signup_fail_label = QtWidgets.QLabel(self.centralwidget)
        self.signup_fail_label.setEnabled(True)
        self.signup_fail_label.setGeometry(QtCore.QRect(95, 320, 285, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.signup_fail_label.setFont(font)
        self.signup_fail_label.setStyleSheet("color:rgb(255, 0, 0)")
        self.signup_fail_label.setObjectName("signup_fail_label")
        self.confirm_fail_label = QtWidgets.QLabel(self.centralwidget)
        self.confirm_fail_label.setEnabled(True)
        self.confirm_fail_label.setGeometry(QtCore.QRect(95, 320, 285, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.confirm_fail_label.setFont(font)
        self.confirm_fail_label.setStyleSheet("color:rgb(255, 0, 0)")
        self.confirm_fail_label.setObjectName("confirm_fail_label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title_label.setText(_translate("MainWindow", "FileSpace"))
        self.username_label.setText(_translate("MainWindow", "Username"))
        self.password_label.setText(_translate("MainWindow", "Create Password"))
        self.confirm_password_label.setText(_translate("MainWindow", "Confirm Password"))
        self.create_account_button.setText(_translate("MainWindow", "Create Account"))
        self.back_button.setText(_translate("MainWindow", "Back"))
        self.signup_fail_label.setText(_translate("MainWindow", "Signup Failed - Username already exists"))
        self.confirm_fail_label.setText(_translate("MainWindow", "Signup Failed - Couldn\'t confirm password"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiSignup()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
