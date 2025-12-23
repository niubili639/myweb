from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.modules.auth import schemas
from app.modules.auth.models import ApiKey, User


def _validate_invite(invite_code: str, settings) -> bool:
    today_code = f"{settings.invite_secret}-{datetime.now().strftime('%Y%m%d')}"
    return invite_code == today_code or invite_code == settings.invite_secret


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> User:
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    is_first_user = db.query(User).count() == 0
    settings = get_settings()
    if not is_first_user and not _validate_invite(user_in.invite_code, settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired invite code")

    role = "admin" if is_first_user else "user"
    allowed_spaces = "couple,family,friends,ai" if role == "admin" else "couple"
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_admin=user_in.is_admin or is_first_user,
        role=role,
        allowed_spaces=allowed_spaces,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def set_api_key(db: Session, provider: str, key: str) -> ApiKey:
    api_key = db.query(ApiKey).filter(ApiKey.provider == provider).first()
    if api_key:
        api_key.key = key
    else:
        api_key = ApiKey(provider=provider, key=key)
        db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


def get_api_key(db: Session, provider: str) -> ApiKey | None:
    return db.query(ApiKey).filter(ApiKey.provider == provider).first()


def list_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()


def update_user(
    db: Session,
    user_id: int,
    role: str | None = None,
    allowed_spaces: str | None = None,
) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if role:
        user.role = role
        user.is_admin = role == "admin" or role == "manager"
    if allowed_spaces is not None:
        user.allowed_spaces = allowed_spaces
    db.commit()
    db.refresh(user)
    return user
