from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint, Text

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), default="user", nullable=False)
    allowed_spaces = Column(Text, default="couple", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (UniqueConstraint("provider", name="uq_api_keys_provider"),)

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    key = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
