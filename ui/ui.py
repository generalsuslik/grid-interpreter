import logging
import threading
import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon

from .editor import Editor
from .field import Field
from .settings import Settings


# crutch for normal button generation
class OpenHelper:
    def __init__(self, fname, s):
        self.fname = fname
        self.s = s

    def __call__(self, event):
        self.s.open_file(event=event, filename=self.fname)


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, interpreter, parent=None):
        super().__init__()
        self.interpreter = interpreter
        self.parent = parent
        self.stop_img = QIcon("./ui/assets/stop-icon.png")
        self.run_img = QIcon("./ui/assets/run-icon.png")
        self.force_stop = False

    def run(self):
        self.force_stop = False
        self.interpreter.force_stop = False
        self.parent.run_btn.setStyleSheet("""
            QPushButton {
                border-radius: 4px;
                background: rgb(170, 60, 60);
            }

            QPushButton:hover {
                border-radius: 4px;
                background: rgb(180, 70, 70);
            }

            QPushButton:pressed  {
                border-radius: 4px;
                background: rgb(190, 77, 77);
            }
        """)
        self.parent.run_btn.setIcon(self.stop_img)
        try:
            self.parent.way = self.interpreter.execute(self.parent.filename)
            if not self.force_stop:
                result_x, result_y = self.parent.way[-1][0], self.parent.way[-1][1]
                self.parent.cords.setText(f"X: {result_x}\n Y: {result_y}")
                self.parent.log(self.parent.way)
        except Exception as ex:
            self.parent.cords.setText("X: ---\nY: ---")
            self.parent.way = []
            self.parent.log(ex, level=logging.ERROR)
        if not self.force_stop:
            self.parent.preview.update(self.parent.way)
        self.repaint_btn_back()
        self.finished.emit()

    def repaint_btn_back(self):
        self.parent.run_btn.setStyleSheet("""
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
        self.parent.run_btn.setIcon(self.run_img)

    def stop_it(self):
        try:
            self.force_stop = True
            self.interpreter.force_stop = True

        except Exception as ex:
            print(ex)


class Ui(QtWidgets.QMainWindow):
    def __init__(self, interpreter, db_manager, logger):
        super(Ui, self).__init__()
        self.db = db_manager
        self.logger = logger
        self.interpreter = interpreter

        # load settings
        self.config = self.db.get_settings()
        self.save_on_close = self.config.get("save_on_exit", "1") == "1"
        self.default_filename = self.config.get("default_filename", "program")
        self.editor_font_family = self.config.get(
            "font_name",
            "Cascadia Code"
        )
        self.editor_font_size = int(self.config.get("font_size", "12"))

        # lets build UI
        uic.loadUi("./ui/main.ui", self)
        self.setWindowTitle("Grid Master")
        self.open_file_btn.clicked.connect(self.open_file)
        self.new_file_btn.clicked.connect(self.create_file)
        self.save_file_btn.clicked.connect(self.save_file)
        self.settings_btn.clicked.connect(self.open_settings)
        self.run_btn.clicked.connect(self.execute_code)
        self.code_field = Editor(self)
        self.code_layout.addWidget(self.code_field)
        self.default_log_style = self.logs.currentCharFormat()
        self.preview = Field(self, 21)
        self.cords = QtWidgets.QLabel("X: 0\nY: 0")
        self.cords.setStyleSheet("font-size: 12pt; font-weight: 700;")
        self.cords.setAlignment(Qt.AlignCenter)
        self.preview_layout.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.preview)
        self.preview_layout.addWidget(self.cords)

        self.filename = ""
        self.way = None
        self.recent_layout.setAlignment(Qt.AlignTop)
        self.generate_recent()
        self.show()
        self.preview.update()

        # set up multithreading
        self.thread = QThread()
        self.worker = Worker(self.interpreter, self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)

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

    def open_file(self, event=None, filename=""):
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
            for i in range(self.recent_layout.count() - 1, 0, -1):
                self.recent_layout.itemAt(i).widget().deleteLater()
            self.generate_recent()
            self.code_field.lexer.styleText(0, len(code))
        else:
            self.log("You didn't select a file")

    def create_file(self, event=None):
        self.filename = ""
        self.code_field.setText("")

    def save_file(self, event=None):
        if not self.filename:
            self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                directory=self.default_filename,
                filter="*.txt"
            )
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(self.code_field.text())
                self.db.update_recent(self.filename, time.time())

    def execute_code(self, event=None):
        self.save_file(None)
        if self.thread.isRunning():
            self.worker.stop_it()
        else:
            self.thread.start()

    def log(self, text, level=logging.INFO):
        self.logger.log(
            level=level,
            msg=text
        )
        log_cursor = self.logs.textCursor()  # Moving cursor to the end before
        log_cursor.movePosition(11)          # writing new log line to avoid a
        self.logs.setTextCursor(log_cursor)  # bug if user clicked on logfield
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

    def open_settings(self, event=None):
        self.settings_dialog = Settings(self.db, self)
        self.settings_dialog.show()

    def resizeEvent(self, event=None):
        super().resizeEvent(event)
        self.preview.update(self.way)

    def closeEvent(self, event=None):
        if self.save_on_close:
            self.save_file()
