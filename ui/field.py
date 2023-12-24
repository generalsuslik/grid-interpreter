from PyQt5.QtWidgets import QLabel


class Field(QLabel):
    def __init__(self, parent, cell_num=21):
        super(Field, self).__init__()
        self.parent = parent
        self.setStyleSheet("""
        background-color:grey;
        """)

    def update(self):
        self.size = int(self.parent.preview_layout.geometry().width() * 0.96)
        self.setMinimumSize(self.size, self.size)
        self.parent.preview_layout.update()
