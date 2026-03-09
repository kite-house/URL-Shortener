from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import random

class Settings(BaseSettings):
    MODE: str

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int 

    APP_NAME: str = "URL-Shortener"
    VERSION: str = "1.0.0"

    API_BASE_URL: str = "http://127.0.0.1:8000"

    SLUG_MIN_LENGTH: int = 3
    SLUG_MAX_LENGTH: int = 10

    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file = ".env"
    )

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_DATA(self):
        return self.REDIS_HOST, self.REDIS_PORT
    
    @property
    def RANDOM_SLUG_LENGTH(self):
        return random.randint(self.SLUG_MIN_LENGTH, self.SLUG_MAX_LENGTH)
    

settings = Settings()