from PyQt5 import QtWidgets, QtCore
import sys
import os


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.treeView = QtWidgets.QTreeView(self)
        self.setCentralWidget(self.treeView)

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('C:\\Users\\orico\\OneDrive\\שולחן העבודה\\ServerFolder\\')
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index('C:\\Users\\orico\\OneDrive\\שולחן העבודה\\ServerFolder\\'))


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
