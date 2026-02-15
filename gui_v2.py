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

from config_manager import ConfigManager
from config_dialog import ConfigDialog

logger = logging.getLogger("excel_app")
logger.setLevel(logging.DEBUG)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, app_context, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_context = app_context
        self.setupUi(self)
        self.current_df = None
        self.current_file_path = None
        

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

        self.action_saveas_2.triggered.connect(self.save_as_file)

        self.action_configuration_2.triggered.connect(self.open_configuration)


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

        # сохранение логов в файл
        log_file_path = self.app_context.session_dir / "log.txt"
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )

        logger.addHandler(file_handler)

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
            self.current_df = df
            self.current_file_path = path
            model = PandasModel(df)
            self.tableView.setModel(model)
            self.tableView.resizeColumnsToContents()

            logger.info(
                f"Файл успешно загружен (строк: {df.shape[0]}, столбцов: {df.shape[1]})"
            )

        except Exception as e:
            logger.exception("Ошибка при загрузке Excel файла")
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))

    def save_as_file(self):
        if self.current_df is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Предупреждение",
                "Нет файла для сохранения"
            )
            logger.warning("Попытка сохранить без файла")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как",
            "",
            "Excel Files (*.xlsx)"
        )

        if file_path:
            try:
                self.current_df.to_excel(file_path, index=False)

                logger.info(f"Файл успешно сохранён как: {file_path}")

                QtWidgets.QMessageBox.information(
                    self,
                    "Успешно",
                    "Файл успешно сохранён"
                )

            except Exception as e:
                logger.exception("Ошибка при сохранении файла")
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка сохранения",
                    str(e)
              )        
    def open_configuration(self):
        from config_dialog import ConfigDialog

        dialog = ConfigDialog(self.config_manager)
        dialog.exec()

    def show_logs(self):
          self.log_window.show()
          self.log_window.raise_()
          self.log_window.activateWindow()

    def closeEvent(self, event):
        logger.removeHandler(self.qt_log_handler)
        self.qt_log_handler.close()
        super().closeEvent(event)
      
   


def run_gui(app_context):
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    config_manager = ConfigManager(app_context)

    # проверка при запуске
    if not config_manager.get_api_key():
        dialog = ConfigDialog(config_manager)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return  # если пользователь закрыл окно    

    window = MainWindow(app_context=app_context)
    window.config_manager = config_manager
    window.show()

    app.exec()