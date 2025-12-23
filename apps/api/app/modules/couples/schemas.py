from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


# ========== Couple ==========
class CoupleCreate(BaseModel):
    name: str
    start_date: date | None = None
    partner_a_name: str | None = None
    partner_b_name: str | None = None
    partner_a_avatar: str | None = None
    partner_b_avatar: str | None = None
    partner_a_birthday: date | None = None
    partner_b_birthday: date | None = None
    partner_a_location: str | None = None
    partner_b_location: str | None = None


class CoupleRead(BaseModel):
    id: int
    name: str
    start_date: date | None
    partner_a_name: str | None
    partner_b_name: str | None
    partner_a_avatar: str | None
    partner_b_avatar: str | None
    partner_a_birthday: date | None
    partner_b_birthday: date | None
    partner_a_location: str | None
    partner_b_location: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Note ==========
class NoteCreate(BaseModel):
    title: str
    content_md: str


class NoteRead(BaseModel):
    id: int
    title: str
    content_md: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Message (留言板) ==========
class MessageCreate(BaseModel):
    author: str
    content: str


class MessageRead(BaseModel):
    id: int
    author: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Countdown (倒计时) ==========
class CountdownCreate(BaseModel):
    title: str
    target_date: date
    is_yearly: bool = False


class CountdownUpdate(BaseModel):
    title: str | None = None
    target_date: date | None = None
    is_yearly: bool | None = None
    is_pinned: bool | None = None


class CountdownRead(BaseModel):
    id: int
    title: str
    target_date: date
    is_yearly: bool
    is_pinned: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Wish (愿望清单) ==========
class WishCreate(BaseModel):
    title: str
    progress: int = 0


class WishUpdate(BaseModel):
    title: str | None = None
    progress: int | None = None
    completed: bool | None = None
    is_pinned: bool | None = None


class WishRead(BaseModel):
    id: int
    title: str
    progress: int
    completed: bool
    is_pinned: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
