import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPoint, QPropertyAnimation, Qt
from PyQt5.QtGui import QFont


class Settings(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super(Settings, self).__init__()
        self.db = db
        self.parent = parent
        self.oldPos = None
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        uic.loadUi("./ui/settings.ui", self)
        self.close_btn.clicked.connect(self.close)
        # setting up animation
        self.fade_in_anim = QPropertyAnimation(self, b'windowOpacity')
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.setDuration(200)
        self.setWindowOpacity(0)
        # set current settings
        try:
            self.settings = self.db.get_settings()
            self.default_filename_edit.setText(
                self.settings.get("default_filename", "program.txt")
            )
            self.save_on_exit_checkbox.setChecked(
                self.settings.get("save_on_exit", "1") == "1"
            )
            self.font_size_spin.setValue(
                int(self.settings.get("font_size", 12))
            )
            font = QFont(
                self.settings.get("font_name", "Cascadia Code")
            )
            self.font_select.setCurrentFont(font)
        except Exception as e:
            self.parent.log(e)

    def mousePressEvent(self, event):
        if event.globalPos().y() <= self.y() + self.navbar.geometry().height():
            self.oldPos = event.globalPos()
        else:
            self.oldPos = None

    def smooth_appearance(self):
        self.fade_in_anim.start()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def closeEvent(self, event):
        font_size = self.font_size_spin.value()
        font = self.font_select.currentFont().family()
        default_filename = self.default_filename_edit.text()
        if not default_filename:
            default_filename = "program"
        save_on_exit = self.save_on_exit_checkbox.isChecked()
        self.parent.save_on_close = save_on_exit
        self.parent.default_filename = default_filename
        settings = {
            "font_size": font_size,
            "font_name": font,
            "default_filename": default_filename,
            "save_on_exit": int(save_on_exit)
        }
        try:
            self.db.save_settings(settings)
        except Exception as e:
            self.parent.log(e)
        QtWidgets.QMessageBox.about(
            self.parent,
            "Требуется перезапуск",
            "Перезапустите приложение для применения изменений"
        )
