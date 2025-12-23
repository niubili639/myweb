from typing import List, Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    history: Optional[List[ChatMessage]] = None
    model: Optional[str] = None  # allow override text model
    session_id: Optional[int] = None
    mode: Optional[str] = "chat"


class ChatResponse(BaseModel):
    reply: str
    session_id: Optional[int] = None


class ImageRequest(BaseModel):
    prompt: str
    model: Optional[str] = None  # allow override image model
    size: Optional[str] = None  # e.g., "1024*1024"
    session_id: Optional[int] = None


class ImageResponse(BaseModel):
    images: List[str]
    session_id: Optional[int] = None


class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    mode: str = "chat"
    model: Optional[str] = None


class ChatSessionRead(BaseModel):
    id: int
    title: Optional[str]
    mode: str
    model: Optional[str]
    is_pinned: int = 0
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
