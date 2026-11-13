from pathlib import Path
import json

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


_policy_path = Path(__file__).resolve().parent.parent / "data/pilot/decision-policies/policy.json"
_policy = json.loads(_policy_path.read_text(encoding="utf-8"))["deployment"]


class Settings(BaseSettings):
    DATABASE_URL: str
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    MODEL_REVISION: str = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
    CLASSIFICATION_REFERENCE_SOURCE: str = "pilot_en_120_v1"
    K_NEIGHBORS: int = Field(default=3, ge=1, le=100)
    CATEGORY_MIN_SIMILARITY: float = Field(default=_policy["category_min_similarity"], ge=-1, le=1)
    CATEGORY_MIN_VOTE_SHARE: float = Field(default=_policy["category_min_vote_share"], ge=0, le=1)
    PRIORITY_MIN_SCORE: float = Field(default=_policy["priority_min_score"], ge=0, le=1)
    DUPLICATE_MIN_SIMILARITY: float = Field(default=_policy["duplicate_min_similarity"], ge=-1, le=1)
    DUPLICATE_SAME_CATEGORY: bool = _policy["duplicate_same_category"]
    MAX_DUPLICATE_SUGGESTIONS: int = Field(default=5, ge=1, le=100)
    ESCALATION_ENABLED: bool = True
    ESCALATION_MIN_USERS: int = Field(default=3, ge=2)
    ESCALATION_WINDOW_HOURS: float = Field(default=24, gt=0)
    ESCALATION_MIN_SIMILARITY: float = Field(default=.85, ge=-1, le=1)
    ALLOWED_EMAIL_DOMAIN: str = Field(default="mail.com", pattern=r"^[A-Za-z0-9.-]+$")
    JWT_SECRET_KEY: SecretStr | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg")

    # Stare lokalne pliki mogą jeszcze zawierać CELERY_BROKER_URL.
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env", extra="ignore"
    )


settings = Settings()

