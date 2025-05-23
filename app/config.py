from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str

    # указываем, где искать .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# создаём экземпляр — он подгрузит DATABASE_URL из .env
settings = Settings()

