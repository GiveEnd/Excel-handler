from PyQt6 import QtWidgets

class HistoryDialog(QtWidgets.QDialog):
    def __init__(self, history):
        super().__init__()
        self.setWindowTitle("История")
        self.resize(1100, 500) 

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Тип", "Промт", "Файл", "Начало", "Окончание"
        ])
        self.table.setRowCount(len(history))

        # растягивание колонок на всю ширину
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        for i, record in enumerate(history):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(record.get("type", "")))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(record.get("prompt", "")))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(record.get("file_path", "")))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(record.get("start_time", "")))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(record.get("end_time", "")))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)