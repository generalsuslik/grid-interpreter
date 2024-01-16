from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import QColor, QFont, QFontMetrics

from .highlight import Lexer


class Editor(QsciScintilla):
    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)
        self.parent = parent
        font = QFont(self.parent.editor_font_family)
        font.setFixedPitch(True)
        font.setPointSize(self.parent.editor_font_size)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setUtf8(True)
        self.setColor(QColor("#eeeeee"))

        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000"))
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#202020"))
        self.setMarginsForegroundColor(QColor("#aaaaaa"))
        self.wrapMode()
        self.setMinimumSize(200, 200)
        self.setScrollWidth(1)
        self.ScrollWidthTracking = True

        self.setTabWidth(4)
        self.lexer = Lexer(self)
        self.setLexer(self.lexer)
