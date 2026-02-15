import json
from pathlib import Path
import logging

logger = logging.getLogger("excel_app")

class ConfigManager:
    def __init__(self, app_context):
        self.config_path = app_context.data_dir / "config.json"
        self._config = {}
        self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logger.info("Конфигурация успешно загружена")
            except Exception as e:
                logger.exception("Ошибка при загрузке config.json")
                self._config = {}
        else:
            logger.info("config.json не найден. Будет создан.")
            self._config = {}

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
            logger.info("Конфигурация сохранена")
        except Exception:
            logger.exception("Ошибка при сохранении config.json")

    def get_api_key(self):
        key = self._config.get("api_key", "")
        logger.info(f"Получение API ключа. Есть ли ключ: {bool(key)}")
        return key
    
    def set_api_key(self, value):
        logger.info("Обновление API ключа")
        self._config["api_key"] = value
        self.save()