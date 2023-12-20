import logging
import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from .editor import Editor


# crutch for normal button generation
class OpenHelper:
    def __init__(self, fname, s):
        self.fname = fname
        self.s = s

    def __call__(self, event):
        self.s.open_file(event=event, filename=self.fname)


class Ui(QtWidgets.QMainWindow):
    def __init__(self, interpreter, db_manager, logger):
        super(Ui, self).__init__()
        self.db = db_manager
        self.logger = logger
        self.interpreter = interpreter
        uic.loadUi("./ui/main.ui", self)

        self.open_file_btn.clicked.connect(self.open_file)
        self.new_file_btn.clicked.connect(self.create_file)
        self.save_file_btn.clicked.connect(self.save_file)
        self.settings_btn.clicked.connect(self.open_settings)
        self.run_btn.clicked.connect(self.execute_code)

        self.code_field = Editor(self)
        self.code_layout.addWidget(self.code_field)
        self.default_log_style = self.logs.currentCharFormat()

        self.filename = ""
        self.recent_layout.setAlignment(Qt.AlignTop)
        self.generate_recent()
        self.show()
        self.log("Ida started up")
        self.log("We're ready to go")

    def generate_recent(self):
        recent_files = self.db.get_recent()
        for file in recent_files:
            btn = QtWidgets.QPushButton()
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 4px;
                    background: rgb(50, 50, 50);
                }

                QPushButton:hover {
                    border-radius: 4px;
                    background: rgb(60, 60, 60);
                }

                QPushButton:pressed  {
                    border-radius: 4px;
                    background: rgb(77, 77, 77);
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
                f.write(self.code_field.text())
                self.db.update_recent(self.filename, time.time())

    def execute_code(self, event):
        self.save_file(None)
        try:
            run_result = self.interpreter.execute(self.filename)
            self.log(run_result)
        except Exception as ex:
            self.log(ex, level=logging.ERROR)

    def log(self, text, level=logging.INFO):
        self.logger.log(
            level=level,
            msg=text
        )
        match level:
            case logging.INFO:
                style = self.default_log_style
                style.setForeground(QColor(160, 255, 160))
                self.logs.setCurrentCharFormat(style)
            case logging.WARNING:
                style = self.default_log_style
                style.setForeground(QColor(222, 222, 120))
                self.logs.setCurrentCharFormat(style)
            case logging.ERROR:
                style = self.default_log_style
                style.setForeground(QColor(222, 120, 120))
                self.logs.setCurrentCharFormat(style)
            case logging.CRITICAL:
                style = self.default_log_style
                style.setForeground(QColor(222, 120, 120))
                style.setFontWeight(75)
                self.logs.setCurrentCharFormat(style)
        if level != logging.DEBUG:
            self.logs.insertPlainText(f"Ida> {text}\n")
            self.logs.setCurrentCharFormat(self.default_log_style)

    def open_settings(self, event):
        print("settings")
