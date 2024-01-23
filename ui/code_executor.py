import logging
import os

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon


BASE_DIR = os.path.dirname(__file__)


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, interpreter, parent=None):
        super().__init__()
        self.interpreter = interpreter
        self.parent = parent
        self.stop_img = QIcon(os.path.join(BASE_DIR, "./assets/stop-icon.png"))
        self.run_img = QIcon(os.path.join(BASE_DIR, "./assets/run-icon.png"))
        self.run_slow_img = QIcon(os.path.join(BASE_DIR, "./assets/run-animated-icon.png"))
        self.force_stop = False
        self.animate = False
        self.drawing = False

    def run(self):
        self.paint_btn()
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
            self.drawing = True
            if self.animate:
                if len(self.parent.way) < 100:
                    self.parent.preview.update(self.parent.way, 0.01)
                else:
                    self.parent.log("The way is too long to be animated")
                    self.parent.preview.update(self.parent.way)
            else:
                self.parent.preview.update(self.parent.way)
            self.drawing = False
        self.repaint_btn_back()
        self.force_stop = False
        self.interpreter.force_stop = False
        self.finished.emit()

    def paint_btn(self):
        style = """
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
        """
        self.parent.run_btn.setStyleSheet(style)
        self.parent.run_slowly_btn.setStyleSheet(style)
        self.parent.run_btn.setIcon(self.stop_img)
        self.parent.run_slowly_btn.setIcon(self.stop_img)

    def repaint_btn_back(self):
        style = """
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
                """

        self.parent.run_btn.setStyleSheet(style)
        self.parent.run_slowly_btn.setStyleSheet(style)
        self.parent.run_btn.setIcon(self.run_img)
        self.parent.run_slowly_btn.setIcon(self.run_slow_img)

    def stop_it(self):
        try:
            self.force_stop = True
            self.interpreter.force_stop = True
        except Exception as ex:
            self.parent.log(ex, level=logging.ERROR)
