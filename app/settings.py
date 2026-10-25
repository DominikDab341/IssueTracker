from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    MODEL_NAME: str = "all-MiniLM-L6-v2"

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg")

    # Stare lokalne pliki mogą jeszcze zawierać CELERY_BROKER_URL.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

