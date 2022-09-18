from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow, QLabel, QPlainTextEdit
import os


class CrashReport(QMainWindow):
    def __init__(self, guupath, err, parent=None):
        super(CrashReport, self).__init__()

        print("GUU: Showing crash report 1")
        loadUi(os.path.join(guupath, "ui", "crash.ui"), self)

        self.output.insertPlainText(err)
