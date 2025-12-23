from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PhotoCreate(BaseModel):
    url: str
    thumbnail_url: str | None = None
    caption: str | None = None
    image_key: str | None = None
    space_type: str = "couple"
    space_id: int | None = None


class PhotoRead(BaseModel):
    id: int
    url: str
    thumbnail_url: str | None
    caption: str | None
    image_key: str | None
    space_type: str
    space_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
