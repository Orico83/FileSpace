# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(854, 605)
        self.horizontalLayout = QtWidgets.QHBoxLayout(MainWindow)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabs = QtWidgets.QTabWidget(MainWindow)
        self.tabs.setEnabled(True)
        self.tabs.setObjectName("tabs")
        self.myfolder_tab = QtWidgets.QWidget()
        self.myfolder_tab.setObjectName("myfolder_tab")
        self.upload_files_button = QtWidgets.QPushButton(self.myfolder_tab)
        self.upload_files_button.setGeometry(QtCore.QRect(730, 80, 81, 23))
        self.upload_files_button.setObjectName("upload_files_button")
        self.share_button = QtWidgets.QPushButton(self.myfolder_tab)
        self.share_button.setGeometry(QtCore.QRect(730, 240, 81, 23))
        self.share_button.setObjectName("share_button")
        self.upload_folders_button = QtWidgets.QPushButton(self.myfolder_tab)
        self.upload_folders_button.setGeometry(QtCore.QRect(730, 120, 81, 23))
        self.upload_folders_button.setObjectName("upload_folders_button")
        self.create_folder_button = QtWidgets.QPushButton(self.myfolder_tab)
        self.create_folder_button.setGeometry(QtCore.QRect(730, 200, 81, 23))
        self.create_folder_button.setObjectName("create_folder_button")
        self.create_file_button = QtWidgets.QPushButton(self.myfolder_tab)
        self.create_file_button.setGeometry(QtCore.QRect(730, 160, 81, 23))
        self.create_file_button.setObjectName("create_file_button")
        self.go_back_button = QtWidgets.QPushButton(self.myfolder_tab)
        self.go_back_button.setGeometry(QtCore.QRect(5, 10, 61, 23))
        self.go_back_button.setObjectName("go_back_button")
        self.list_view = QtWidgets.QListView(self.myfolder_tab)
        self.list_view.setGeometry(QtCore.QRect(70, 10, 641, 541))
        self.list_view.setAcceptDrops(True)
        self.list_view.setDragEnabled(False)
        self.list_view.setDragDropOverwriteMode(False)
        self.list_view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.list_view.setDefaultDropAction(QtCore.Qt.TargetMoveAction)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_view.setIconSize(QtCore.QSize(0, 0))
        self.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.list_view.setObjectName("list_view")
        self.tabs.addTab(self.myfolder_tab, "")
        self.friends_tab = QtWidgets.QWidget()
        self.friends_tab.setObjectName("friends_tab")
        self.friends_list_widget = QtWidgets.QListWidget(self.friends_tab)
        self.friends_list_widget.setGeometry(QtCore.QRect(10, 30, 256, 500))
        self.friends_list_widget.setObjectName("friends_list_widget")
        self.friends_label = QtWidgets.QLabel(self.friends_tab)
        self.friends_label.setGeometry(QtCore.QRect(10, 3, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.friends_label.setFont(font)
        self.friends_label.setObjectName("friends_label")
        self.friend_requests_list_widget = QtWidgets.QListWidget(self.friends_tab)
        self.friend_requests_list_widget.setGeometry(QtCore.QRect(290, 30, 256, 500))
        self.friend_requests_list_widget.setObjectName("friend_requests_list_widget")
        self.friend_requests_label = QtWidgets.QLabel(self.friends_tab)
        self.friend_requests_label.setGeometry(QtCore.QRect(290, 3, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.friend_requests_label.setFont(font)
        self.friend_requests_label.setObjectName("friend_requests_label")
        self.search_results_list = QtWidgets.QListWidget(self.friends_tab)
        self.search_results_list.setGeometry(QtCore.QRect(570, 59, 256, 471))
        self.search_results_list.setObjectName("search_results_list")
        self.search_users_label = QtWidgets.QLabel(self.friends_tab)
        self.search_users_label.setGeometry(QtCore.QRect(570, 3, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.search_users_label.setFont(font)
        self.search_users_label.setObjectName("search_users_label")
        self.search_bar = QtWidgets.QLineEdit(self.friends_tab)
        self.search_bar.setGeometry(QtCore.QRect(660, 5, 151, 20))
        self.search_bar.setText("")
        self.search_bar.setObjectName("search_bar")
        self.search_users_button = QtWidgets.QPushButton(self.friends_tab)
        self.search_users_button.setGeometry(QtCore.QRect(700, 30, 75, 23))
        self.search_users_button.setObjectName("search_users_button")
        self.tabs.addTab(self.friends_tab, "")
        self.horizontalLayout.addWidget(self.tabs)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.upload_files_button.setText(_translate("MainWindow", "Upload Files"))
        self.share_button.setText(_translate("MainWindow", "Share"))
        self.upload_folders_button.setText(_translate("MainWindow", "Upload Folders"))
        self.create_folder_button.setText(_translate("MainWindow", "Create Folder"))
        self.create_file_button.setText(_translate("MainWindow", "Create File"))
        self.go_back_button.setText(_translate("MainWindow", "Back"))
        self.tabs.setTabText(self.tabs.indexOf(self.myfolder_tab), _translate("MainWindow", "My Folder"))
        self.friends_label.setText(_translate("MainWindow", "Friends"))
        self.friend_requests_label.setText(_translate("MainWindow", "Friend Requests"))
        self.search_users_label.setText(_translate("MainWindow", "Find Users"))
        self.search_users_button.setText(_translate("MainWindow", "Search"))
        self.tabs.setTabText(self.tabs.indexOf(self.friends_tab), _translate("MainWindow", "Friends"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
