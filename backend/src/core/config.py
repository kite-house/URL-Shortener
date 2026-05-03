from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Tuple
from functools import lru_cache
from pathlib import Path
import random


ROOT_DIR = Path(__file__).parent.parent.parent.parent
DOTENV = ROOT_DIR / '.env'

class Settings(BaseSettings):
    MODE: str

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int 
    REDIS_PASSWORD: str
    REDIS_CACHE_TTL: int = 86400  # 24 часа

    APP_NAME: str = "URL-Shortener"
    VERSION: str = "1.0.0"

    API_BASE_URL: str = "http://127.0.0.1:8000"

    SLUG_MIN_LENGTH: int = 3
    SLUG_MAX_LENGTH: int = 10

    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REDIS_DB: int = 1

    RATE_LIMIT_RULES: Dict[str, Tuple[int, int, str]] = {
        "/*": (100, 3600, "moving"),           # Глобально: 100 запросов/час
        "/api/shorten": (10, 60, "fixed"),     # Создание ссылок: 10/мин
        "/api/info/*": (60, 60, "moving"),     # Информация: 60/мин
        "/{slug}": (120, 60, "moving"),        # Редирект: 120/мин
    }
    
    # Автобан
    RATE_LIMIT_BAN_OFFENSES: int = 15      # Кол-во нарушений до бана
    RATE_LIMIT_BAN_LENGTH: str = "3m"      # Длительность бана
    RATE_LIMIT_SITE_BAN: bool = True       # Блокировать весь сайт
    
    
    model_config = SettingsConfigDict(
        env_file= str(DOTENV),
        env_file_encoding='utf-8',
        extra='ignore' 
    )

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings

settings = get_settings()
