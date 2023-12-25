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

    def update(self, way=None):
        self.size = int(min(
            self.parent.preview_layout.geometry().width(),
            self.parent.preview_layout.geometry().height()
        ) * 0.96)
        self.setMinimumSize(self.size, self.size)
        self.parent.preview_layout.update()
        self.way = way
        self.render()

    def render(self):
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
                x_start = int(self.way[i][0] * step + step / 2)
                y_start = int(self.way[i][1] * step + step / 2)
                x_end = int(self.way[i + 1][0] * step + step / 2)
                y_end = int(self.way[i + 1][1] * step + step / 2)
                painter.drawLine(x_start, y_start, x_end, y_end)
        painter.end()
        self.setPixmap(canvas)

    def mousePressEvent(self, event):
        if (datetime.now() - self.last_click).total_seconds() < 0.5:
            pass  # show large preview on doubleclick
        else:
            self.last_click = datetime.now()
