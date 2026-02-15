from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox
)


class ConfigDialog(QDialog):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("Конфигурация API")
        self.setMinimumSize(1000, 100)
        self.config_manager = config_manager

        layout = QVBoxLayout(self)

        self.label = QLabel("Введите API ключ:")
        layout.addWidget(self.label)

        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_input)

        self.save_button = QPushButton("Сохранить")
        layout.addWidget(self.save_button)

        current_key = self.config_manager.get_api_key()
        if current_key:
            self.api_input.setText(current_key)

        self.save_button.clicked.connect(self.save_key)

    def save_key(self):
        api_key = self.api_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Ошибка", "Добавьте API ключ")
            return

        self.config_manager.set_api_key(api_key)
        self.accept()