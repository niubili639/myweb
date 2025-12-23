from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PhotoCreate(BaseModel):
    url: str
    caption: str | None = None


class PhotoRead(BaseModel):
    id: int
    url: str
    caption: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
