from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
import os

class DropLabel(QLabel):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        path = url.toLocalFile()

        if path.lower().endswith((".xlsx", ".xls")):
            self.fileDropped.emit(path)