import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt


# crutch for normal button generation
class OpenHelper:
    def __init__(self, fname, s):
        self.fname = fname
        self.s = s

    def __call__(self, event):
        self.s.open_file(event=event, filename=self.fname)


class Ui(QtWidgets.QMainWindow):
    def __init__(self, db_manager):
        super(Ui, self).__init__()
        self.db = db_manager
        uic.loadUi("./ui/main.ui", self)
        self.open_file_btn.clicked.connect(self.open_file)
        self.new_file_btn.clicked.connect(self.create_file)
        self.save_file_btn.clicked.connect(self.save_file)
        self.settings_btn.clicked.connect(self.open_settings)
        self.filename = ""
        self.recent_layout.setAlignment(Qt.AlignTop)
        self.generate_recent()
        self.show()

    def generate_recent(self):
        recent_files = self.db.get_recent()
        for file in recent_files:
            btn = QtWidgets.QPushButton()
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 4px;
                    background: rgb(50, 50, 50);
                    aspect-ratio: 1;
                }

                QPushButton:hover {
                    border-radius: 4px;
                    background: rgb(60, 60, 60);
                    aspect-ratio: 1;
                }

                QPushButton:pressed  {
                    border-radius: 4px;
                    background: rgb(77, 77, 77);
                    aspect-ratio: 1;
                }
            """)
            btn.setText(file[1].split("/")[-1])
            fn = file[1]
            # btn.clicked.connect(lambda event: self.open_file(event, fn))
            # works with bugs, and we need to use additional class
            btn.clicked.connect(OpenHelper(fn, self))
            btn.setMinimumSize(32, 32)
            self.recent_layout.addWidget(btn)

    def open_file(self, event, filename=""):
        if not filename:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                None, "Open File", "./", "File with code (*.txt)"
            )
        if filename:
            self.filename = filename
            with open(self.filename, "r", encoding="utf-8") as f:
                code = f.read()
            self.code_field.setText(code)
            self.db.update_recent(self.filename, time.time())

    def create_file(self, event):
        self.filename = ""
        self.code_field.setText("")

    def save_file(self, event):
        if not self.filename:
            self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                filter="*.txt"
            )
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(self.code_field.toPlainText())
                self.db.update_recent(self.filename, time.time())

    def open_settings(self, event):
        print("settings")
