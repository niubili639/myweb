from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_token
from app.db.session import get_db
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import TokenPayload

settings = get_settings()
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db_session() -> Generator:
    yield from get_db()


def get_current_user(db: Session = Depends(get_db_session), token: str = Depends(reusable_oauth2)):
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    if not token_data.sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = auth_service.get_user_by_id(db, user_id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_admin(current_user=Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user
