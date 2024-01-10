from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt


class Settings(QtWidgets.QMainWindow):
    def __init__(self):
        super(Settings, self).__init__()
        self.setWindowModality(Qt.ApplicationModal)
        uic.loadUi("./ui/settings.ui", self)
