from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core import deps
from app.core.security import create_access_token
from app.core.logging import logger
from app.modules.auth import schemas, service

router = APIRouter()


@router.post("/register", response_model=schemas.UserRead, summary="Register user (requires invite)")
def register_user(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db_session)):
    logger.info(f"Register attempt email={user_in.email}")
    user = service.create_user(db, user_in)
    logger.info(f"Register success user_id={user.id}")
    return user


@router.post("/login", response_model=schemas.LoginResponse, summary="Login to get JWT")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db_session)
):
    logger.info(f"Login attempt email={form_data.username}")
    user = service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        logger.warning("Login failed: bad credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token = create_access_token(subject=user.id)
    logger.info(f"Login success user_id={user.id}")
    return schemas.LoginResponse(token=schemas.Token(access_token=access_token), user=user)


@router.get("/me", response_model=schemas.UserRead, summary="Get current user")
def read_me(current_user=Depends(deps.get_current_active_user)):
    logger.debug(f"Fetch current user user_id={current_user.id}")
    return current_user


@router.post(
    "/apikey",
    response_model=schemas.ApiKeyRead,
    summary="Set provider API key (admin)",
)
def set_provider_key(
    payload: schemas.ApiKeyCreate,
    db: Session = Depends(deps.get_db_session),
    _: schemas.UserRead = Depends(deps.get_current_admin),
):
    logger.info(f"Set API key provider={payload.provider}")
    api_key = service.set_api_key(db, provider=payload.provider, key=payload.key)
    return schemas.ApiKeyRead(provider=api_key.provider, key=api_key.key)


@router.get(
    "/apikey/{provider}",
    response_model=schemas.ApiKeyRead,
    summary="Get provider API key (admin)",
)
def get_provider_key(
    provider: str,
    db: Session = Depends(deps.get_db_session),
    _: schemas.UserRead = Depends(deps.get_current_admin),
):
    logger.debug(f"Get API key provider={provider}")
    api_key = service.get_api_key(db, provider=provider)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return schemas.ApiKeyRead(provider=api_key.provider, key=api_key.key)


@router.get("/users", response_model=list[schemas.UserRead], summary="List users (admin)")
def list_users(db: Session = Depends(deps.get_db_session), _: schemas.UserRead = Depends(deps.get_current_admin)):
    return service.list_users(db)


class UserUpdate(BaseModel):
    role: str | None = None
    allowed_spaces: str | None = None


@router.patch(
    "/users/{user_id}",
    response_model=schemas.UserRead,
    summary="Update user role/spaces (admin)",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(deps.get_db_session),
    _: schemas.UserRead = Depends(deps.get_current_admin),
):
    return service.update_user(db, user_id=user_id, role=payload.role, allowed_spaces=payload.allowed_spaces)
