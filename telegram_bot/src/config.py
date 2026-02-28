from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str

    model_config = SettingsConfigDict(
        env_file = ".env",
    )

    @property
    def GET_TOKEN(self):
        return self.TELEGRAM_TOKEN
    
settings = Settings()