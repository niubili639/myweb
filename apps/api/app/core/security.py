from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def _truncate_password(password: str) -> str:
    # bcrypt accepts up to 72 bytes; ensure UTF-8 bytes are within limit
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = _truncate_password(plain_password)
    return pwd_context.verify(safe_password, hashed_password)


def get_password_hash(password: str) -> str:
    safe_password = _truncate_password(password)
    return pwd_context.hash(safe_password)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise exc
