from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    ALLOWED_EMAIL_DOMAIN: str = Field(default="mail.com", pattern=r"^[A-Za-z0-9.-]+$")
    JWT_SECRET_KEY: SecretStr | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg")

    # Stare lokalne pliki mogą jeszcze zawierać CELERY_BROKER_URL.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

