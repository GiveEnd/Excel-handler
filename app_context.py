import os
from pathlib import Path
from datetime import datetime

class AppContext:
    """Хранит все пути и данные для текущей сессии приложения"""
    def __init__(self, base_dir, data_dir, sessions_dir, session_dir, save_dir):
        self.base_dir = base_dir            # папка с exe
        self.data_dir = data_dir            # handler data
        self.sessions_dir = sessions_dir    # sessions
        self.session_dir = session_dir      # текущая сессия
        self.save_dir = save_dir            # папка для сохранения результатов внутри сессии

def init_app_context():
    """
    Создаёт папки:
      handler data
      sessions
      текущая сессия с датой и временем
    Возвращает объект AppContext с путями
    """

    # папка, где находится exe
    base_dir = Path(os.path.abspath(os.path.dirname(__file__)))

    # папка handler data
    data_dir = base_dir / "handler data"
    data_dir.mkdir(exist_ok=True)

    # папка sessions
    sessions_dir = data_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)

    # папка текущей сессии с датой и временем
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_dir = sessions_dir / now
    session_dir.mkdir(exist_ok=True)

    # папка для сохранения результатов внутри сессии
    save_dir = session_dir / "saved files"
    save_dir.mkdir(exist_ok=True)

    # возвращение объекта с путями
    return AppContext(
        base_dir=base_dir,
        data_dir=data_dir,
        sessions_dir=sessions_dir,
        session_dir=session_dir,
        save_dir=save_dir
    )