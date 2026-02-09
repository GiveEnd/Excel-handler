from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Логи")
        self.resize(700, 400)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.text_edit.clear)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.clear_button)
        self.setLayout(layout)

    def append_log(self, message: str):
        self.text_edit.append(message)

    def closeEvent(self, event):
        event.ignore()
        self.hide()    
