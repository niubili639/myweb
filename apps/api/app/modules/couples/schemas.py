from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CoupleCreate(BaseModel):
    name: str
    start_date: date | None = None
    partner_a_name: str | None = None
    partner_b_name: str | None = None


class CoupleRead(BaseModel):
    id: int
    name: str
    start_date: date | None
    partner_a_name: str | None
    partner_b_name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteCreate(BaseModel):
    title: str
    content_md: str


class NoteRead(BaseModel):
    id: int
    title: str
    content_md: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
