import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog
import pandas as pd
import logging
import datetime

from MainWindow import Ui_MainWindow
from drag_drop import DropLabel
from models import PandasModel
from log_window import LogWindow
from qt_log_handler import QtLogHandler

from config_manager import ConfigManager
from config_dialog import ConfigDialog

from history_manager import HistoryManager
from history_dialog import HistoryDialog

import os

logger = logging.getLogger("excel_app")
logger.setLevel(logging.DEBUG)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, app_context, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_context = app_context
        self.setupUi(self)
        self.current_df = None
        self.current_file_path = None

        self.history_manager = HistoryManager(session_dir=self.app_context.session_dir)
        

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

        self.pushButton_start.clicked.connect(self.on_start_clicked)
        self.pushButton_back.clicked.connect(self.go_back)
        self.pushButton_forward.clicked.connect(self.go_forward)
        self.pushButton.clicked.connect(self.show_history)

        self.update_navigation_buttons() # дизайн кнопок истории



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

            # spinbox
            n_rows = len(df)
            self.spinBox.setMaximum(n_rows) # макс значение - кол-во строк в файле
            self.spinBox.setValue(n_rows)

            logger.info(
                f"Файл успешно загружен (строк: {df.shape[0]}, столбцов: {df.shape[1]})"
            )

            # автосохранение файла в папку сессии
            save_file_path = self.app_context.save_dir
            if not os.path.exists(save_file_path):
                os.makedirs(save_file_path)

            base_name = os.path.basename(path)
            # поиск существующих файлов с таким же именем, чтобы проставить индекс
            existing_files = [f for f in os.listdir(save_file_path) if "_uploaded_" in f]
            index = 0
            if existing_files:
                indices = []
                for f in existing_files:
                    try:
                        idx = int(f.split("_uploaded_")[0])
                        indices.append(idx)
                    except:
                        continue
                if indices:
                    index = max(indices) + 1

            input_copy_name = f"{index}_uploaded_{base_name}"
            input_copy_path = os.path.join(save_file_path, input_copy_name)
            df.to_excel(input_copy_path, index=False)

            self.history_manager.add_load_history(path)
            self.update_navigation_buttons()

            logger.info(f"Файл автоматически сохранён: {input_copy_path}")

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

    def on_start_clicked(self):

        prompt_text = self.plainTextEdit.toPlainText().strip()

        if not prompt_text:
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка",
                "Поле ввода не должно быть пустым"
            )
            logger.warning("Попытка запуска обработки с пустым промтом")
            return
        
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.current_df is None:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Файл не загружен")
            logger.warning("Попытка запуска обработки без загруженного файла")
            return
        
        

        logger.info("Запуск обработки файла")

        df = self.current_df
        n_rows = self.spinBox.value()

        save_file_path = self.app_context.save_dir

        # сброс прогрессбара
        self.progressBar.setValue(0)

        try:
            from gigachat_api_question_2 import run

            output_path = run(
                df=df,
                prompt_text=prompt_text,
                num_rows=n_rows,
                save_dir=save_file_path,
                progress_callback=self.update_progress,
                app_context=self.app_context
            )

            # отображение нового файла
            result_df = pd.read_excel(output_path)
            self.current_df = result_df
            model = PandasModel(result_df)
            self.tableView.setModel(model)
            self.tableView.resizeColumnsToContents()

            self.label_filepath.setText("Текущий файл: " + output_path)

            logger.info(f"Создан новый файл: {output_path}")

            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # добавление в историю
            self.history_manager.add_prompt_history(
                prompt=prompt_text,
                file_path=output_path,
                start_time=start_time,
                end_time=end_time
            )
            logger.info("История обновлена: добавлен промт для файла %s", output_path)
            self.update_navigation_buttons()

            self.plainTextEdit.clear()


        except Exception as e:
            logger.exception("Ошибка при обработке")
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))


            # print(f"API ключ: {api_key}")

    def update_progress(self, current, total):
        self.progressBar.setMaximum(total)
        self.progressBar.setValue(current)

    def add_to_history(self, path, description=""):
        self.history_manager.add(path, description)
        self.update_navigation_buttons()


    def go_back(self):
        record = self.history_manager.go_back()
        if record:
            self.load_from_record(record)
        self.update_navigation_buttons()

    def go_forward(self):
        record = self.history_manager.go_forward()
        if record:
            self.load_from_record(record)
        self.update_navigation_buttons()

    def load_from_record(self, record):
        try:
            df = pd.read_excel(record["file_path"])
            self.current_df = df
            self.label_filepath.setText("Текущий файл: " + record["file_path"])
            # обновление таблицы
            model = PandasModel(df)
            self.tableView.setModel(model)
            self.tableView.resizeColumnsToContents()

            # обновление spinBox
            self.spinBox.setMaximum(len(df))
            self.spinBox.setValue(len(df))

            logger.info(f"Файл загружен из истории: {record['file_path']}")
        except Exception as e:
            print("Ошибка загрузки:", e)

    def show_history(self):
        dialog = HistoryDialog(self.history_manager.history)
        dialog.exec()


    def update_navigation_buttons(self):
        self.pushButton_back.setEnabled(self.history_manager.can_go_back())
        self.pushButton_forward.setEnabled(self.history_manager.can_go_forward())


      
   


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