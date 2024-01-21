import time
from datetime import datetime

from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QLabel


class Field(QLabel):
    def __init__(self, parent, cell_num=21):
        super(Field, self).__init__()
        self.parent = parent
        self.cell_num = cell_num
        self.setStyleSheet("border: 4px solid; border-radius: 6px;")
        self.last_click = datetime.now()

    def update(self, way=None, delay=0):
        self.size = int(min(
            self.parent.preview_layout.geometry().width(),
            self.parent.preview_layout.geometry().height()
        ) * 0.96)
        while self.size == 0 and self.parent.isVisible():
            self.size = int(min(
                self.parent.preview_layout.geometry().width(),
                self.parent.preview_layout.geometry().height()
            ) * 0.96)
        self.setMinimumSize(self.size, self.size)
        self.parent.preview_layout.update()
        self.way = way
        self.render_field(delay)

    def render_field(self, delay=0):
        canvas = QPixmap(self.size, self.size)
        canvas.fill(QColor(44, 44, 88))
        painter = QPainter(canvas)
        step = self.size / self.cell_num
        for i in range(1, self.cell_num):
            painter.drawLine(int(step * i), 0, int(step * i), self.size)
            painter.drawLine(0, int(step * i), self.size, int(step * i))
        if self.way:
            painter.setPen(QPen(QColor(111, 180, 111), 3))
            for i in range(len(self.way) - 1):
                if self.parent.worker.force_stop:
                    break
                x_start = int(self.way[i][0] * step)
                y_start = int(self.way[i][1] * step)
                x_end = int(self.way[i + 1][0] * step)
                y_end = int(self.way[i + 1][1] * step)
                y_start = self.size - y_start
                y_end = self.size - y_end
                tx_start = x_start
                ty_start = y_start
                cells_move = abs(
                    self.way[i][0] - self.way[i + 1][0] + self.way[i + 1][0] - self.way[i + 1][1]
                )
                if delay:
                    for k in range(cells_move):
                        tx_end = (x_end - x_start) * k // cells_move + x_start
                        ty_end = (y_end - y_start) * k // cells_move + y_start
                        painter.drawLine(tx_start, ty_start, tx_end, ty_end)
                        tx_start = tx_end
                        ty_start = y_start
                        if self.parent.worker.force_stop:
                            break
                        self.setPixmap(canvas)
                        time.sleep(delay)
                painter.drawLine(x_start, y_start, x_end, y_end)
        painter.end()
        self.setPixmap(canvas)

    def mousePressEvent(self, event):
        if (datetime.now() - self.last_click).total_seconds() < 0.5:
            pass  # show large preview on doubleclick
        else:
            self.last_click = datetime.now()
