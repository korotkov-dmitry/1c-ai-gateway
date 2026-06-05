import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PARENT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    ones_base_url: str = ""
    groq_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=PARENT_DIR / ".env",
        env_file_encoding="utf-8"
    )

    def __init__(self, **values):
        super().__init__(**values)
        # 🔥 Проверяем, запущены ли мы внутри Docker
        is_inside_docker = os.path.exists('/.dockerenv')

        # Если мы в Docker, автоматически заменяем localhost/127.0.0.1
        if is_inside_docker and self.ones_base_url:
            self.ones_base_url = self.ones_base_url.replace("localhost", "host.docker.internal")
            self.ones_base_url = self.ones_base_url.replace("127.0.0.1", "host.docker.internal")


# Инициализируем настройки
settings = Settings()
