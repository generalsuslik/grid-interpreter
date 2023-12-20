import sys

from PyQt5 import QtWidgets

from core_tools.logger import setup_logger
from interpreter.interpreter import Interpreter
from ui.db_bridge import DBManager
from ui.ui import Ui


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    logger = setup_logger()
    db = DBManager()
    interpreter = Interpreter()
    window = Ui(interpreter, db, logger)
    app.exec_()
