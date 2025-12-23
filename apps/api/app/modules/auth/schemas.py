from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    is_admin: bool = False
    invite_code: str


class UserRead(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    role: str | None = None
    allowed_spaces: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None


class LoginResponse(BaseModel):
    token: Token
    user: UserRead


class ApiKeyCreate(BaseModel):
    provider: str = "qwen"
    key: str


class ApiKeyRead(BaseModel):
    provider: str
    key: str

    model_config = ConfigDict(from_attributes=True)
