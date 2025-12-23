from sqlalchemy import Column, Integer, String, UniqueConstraint

from app.db.base import Base


class SimpleKV(Base):
    __tablename__ = "simple_kv"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), nullable=False, unique=True, index=True)
    value = Column(String(255), nullable=False)

    __table_args__ = (UniqueConstraint("key", name="uq_simple_kv_key"),)


from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    mode = Column(String(20), default="chat", nullable=False)  # chat | image
    model = Column(String(100), nullable=True)
    is_pinned = Column(Integer, default=0, nullable=False)  # 1 pinned, 0 normal
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text", nullable=False)  # text | image
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
