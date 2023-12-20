import sys

from PyQt5 import QtWidgets

from interpreter.interpreter import Interpreter
from ui.db_bridge import DBManager
from ui.ui import Ui


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    db = DBManager()
    interpreter = Interpreter()
    window = Ui(interpreter, db)
    app.exec_()
