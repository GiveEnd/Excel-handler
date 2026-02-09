import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog
import pandas as pd
import logging

from MainWindow import Ui_MainWindow
from drag_drop import DropLabel
from models import PandasModel
from log_window import LogWindow
from qt_log_handler import QtLogHandler

logger = logging.getLogger("excel_app")
logger.setLevel(logging.DEBUG)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.drop_label = DropLabel(self.widget)
        self.drop_label.setGeometry(self.label_dropfile.geometry())
        self.drop_label.setStyleSheet(self.label_dropfile.styleSheet())
        self.drop_label.setAlignment(self.label_dropfile.alignment())
        self.drop_label.setText(self.label_dropfile.text())

        self.label_dropfile.deleteLater()
        self.label_dropfile = self.drop_label

        self.pushButton_fileinput.raise_()

        self.drop_label.fileDropped.connect(self.load_excel)
        self.pushButton_fileinput.clicked.connect(self.open_file_dialog)

        # логи
        self.log_window = LogWindow(self)

        self.qt_log_handler = QtLogHandler()
        self.qt_log_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s",
                datefmt="%H:%M:%S"
            )
        )

        self.qt_log_handler.log_signal.connect(
            self.log_window.append_log
        )

        logger.addHandler(self.qt_log_handler)

        self.pushButton_logs.clicked.connect(self.show_logs)

        logger.info("GUI инициализирован")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбор Excel файла",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.load_excel(file_path)

    def load_excel(self, path):
        self.label_filepath.setText("Текущий файл: " + path)
        logger.info(f"Загрузка файла: {path}")

        try:
            df = pd.read_excel(path)
            model = PandasModel(df)
            self.tableView.setModel(model)
            self.tableView.resizeColumnsToContents()

            logger.info(
                f"Файл успешно загружен (строк: {df.shape[0]}, столбцов: {df.shape[1]})"
            )

        except Exception as e:
            logger.exception("Ошибка при загрузке Excel файла")
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))

    def show_logs(self):
          self.log_window.show()
          self.log_window.raise_()
          self.log_window.activateWindow()
   




app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")

window = MainWindow()
window.show()
app.exec()