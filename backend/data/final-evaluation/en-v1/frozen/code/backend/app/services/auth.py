"""Hasła Argon2id i krótkotrwałe tokeny; uprawnienia zawsze pochodzą z bazy."""
from datetime import datetime, timedelta, timezone

import anyio
from email_validator import EmailNotValidError, validate_email
import jwt
from pwdlib import PasswordHash

from app.services.errors import AuthenticationError, InvalidInputError
from app.settings import settings


password_hasher = PasswordHash.recommended()
# Stały hash służy wyłącznie wyrównaniu kosztu błędnego logowania.
_dummy_hash = password_hasher.hash("dummy-login-password-unused")


def normalize_email(value: str) -> str:
    try:
        result = validate_email(value, check_deliverability=False)
    except EmailNotValidError as exc:
        raise InvalidInputError("Podaj poprawny adres e-mail.", field="email") from exc
    if result.domain.lower() != settings.ALLOWED_EMAIL_DOMAIN.lower():
        raise InvalidInputError("Adres e-mail musi należeć do dozwolonej domeny.", field="email")
    return result.normalized.lower()


def validate_password(value: str) -> str:
    if not 12 <= len(value) <= 128:
        raise InvalidInputError("Hasło musi mieć od 12 do 128 znaków.", field="password")
    return value


async def hash_password(value: str) -> str:
    validate_password(value)
    return await anyio.to_thread.run_sync(password_hasher.hash, value)


async def verify_password(value: str, encoded: str | None) -> bool:
    # Ograniczenie dotyczy również formularza logowania, przed kosztownym Argon2.
    if not 1 <= len(value) <= 128:
        return False
    valid = await anyio.to_thread.run_sync(password_hasher.verify, value, encoded or _dummy_hash)
    return valid and encoded is not None


def jwt_secret() -> str:
    value = settings.JWT_SECRET_KEY.get_secret_value() if settings.JWT_SECRET_KEY else ""
    if len(value.encode("utf-8")) < 32:
        raise RuntimeError("Ustaw JWT_SECRET_KEY na losowy sekret o długości co najmniej 32 bajtów.")
    return value


def create_access_token(user_id: int) -> str:
    issued = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user_id), "iat": issued,
                       "exp": issued + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                       "iss": "issuetracker", "aud": "issuetracker-api"}, jwt_secret(), algorithm="HS256")


def read_access_token(token: str) -> int:
    try:
        claims = jwt.decode(token, jwt_secret(), algorithms=["HS256"], issuer="issuetracker",
                            audience="issuetracker-api", options={"require": ["sub", "iat", "exp", "iss", "aud"]})
        user_id = int(claims["sub"])
        if not 1 <= user_id <= 2147483647:
            raise ValueError()
        return user_id
    except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
        raise AuthenticationError("Niepoprawny lub wygasły token. Zaloguj się ponownie.") from exc
