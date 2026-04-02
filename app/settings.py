from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    MODEL_NAME: str = "all-MiniLM-L6-v2"

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg")

    class Config:
        env_file = ".env"


settings = Settings()

