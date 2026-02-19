import json
from pathlib import Path
import datetime

class HistoryManager:
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.history_file_path = self.session_dir / "history.json"
        self.history = []
        self.index = -1
        self.pointer = -1 # для навигации  

        self.create_json()    # создание json, если его нет
        self.load_history()   # загрузка существующей истории

    def create_json(self):
        # создание директории, если нет
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # создание пустого json, если нет
        if not self.history_file_path.exists():
            with open(self.history_file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            with open(self.history_file_path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
                self.index = len(self.history) - 1
        except Exception:
            self.history = []
            self.index = -1

    def save_history(self):
        with open(self.history_file_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def can_go_back(self):
        return self.pointer > 0

    def can_go_forward(self):
        return self.pointer < len(self.history) - 1

    def go_back(self):
        if self.pointer > 0:
            self.pointer -= 1
            return self.history[self.pointer]
        return None

    def go_forward(self):
        if self.pointer < len(self.history) - 1:
            self.pointer += 1
            return self.history[self.pointer]
        return None

    def get_current(self):
        if self.index >= 0 and self.index < len(self.history):
            return self.history[self.index]
        return None

    def add_load_history(self, file_path: str):
        """История загрузки файла"""
        # print(type(file_path))
        file_path = file_path.replace("/", "\\")
        file_path = file_path[0].lower() + file_path[1:]

        record = {
            "index": len(self.history),
            "type": "Загрузка",
            "prompt": "",
            "file_path": file_path,
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": ""
        }

        self.history.append(record)
        self.index += 1
        self.pointer = self.index
        self.save_history()

    def add_prompt_history(self, prompt: str, file_path: str, start_time: str, end_time: str):
        """История с промтом"""
        # print(type(file_path))
        file_path_str = str(file_path)
        record = {
            "index": len(self.history),
            "type": "Промт",
            "prompt": prompt,
             "file_path": file_path_str,
            "start_time": start_time,
            "end_time": end_time
        }

        self.history.append(record)
        self.index += 1
        self.pointer = self.index
        self.save_history()