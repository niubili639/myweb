from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Couple(Base):
    __tablename__ = "couples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    partner_a_name = Column(String(100), nullable=True)
    partner_b_name = Column(String(100), nullable=True)
    partner_a_avatar = Column(Text, nullable=True)
    partner_b_avatar = Column(Text, nullable=True)
    partner_a_birthday = Column(Date, nullable=True)
    partner_b_birthday = Column(Date, nullable=True)
    partner_a_location = Column(String(200), nullable=True)
    partner_b_location = Column(String(200), nullable=True)
    start_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("CoupleNote", back_populates="couple", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="couple", cascade="all, delete-orphan")
    messages = relationship("CoupleMessage", back_populates="couple", cascade="all, delete-orphan")
    countdowns = relationship("CoupleCountdown", back_populates="couple", cascade="all, delete-orphan")
    wishes = relationship("CoupleWish", back_populates="couple", cascade="all, delete-orphan")


class CoupleNote(Base):
    __tablename__ = "couple_notes"

    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content_md = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    couple = relationship("Couple", back_populates="notes")


class CoupleMessage(Base):
    """留言板"""
    __tablename__ = "couple_messages"

    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False, index=True)
    author = Column(String(50), nullable=False)  # 留言者名字
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    couple = relationship("Couple", back_populates="messages")


class CoupleCountdown(Base):
    """纪念日/倒计时"""
    __tablename__ = "couple_countdowns"

    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    target_date = Column(Date, nullable=False)
    is_yearly = Column(Boolean, default=False)  # 是否每年重复（如生日）
    is_pinned = Column(Boolean, default=False)  # 是否置顶
    created_at = Column(DateTime, default=datetime.utcnow)

    couple = relationship("Couple", back_populates="countdowns")


class CoupleWish(Base):
    """愿望清单/待办"""
    __tablename__ = "couple_wishes"

    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    progress = Column(Integer, default=0)  # 0-100
    completed = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)  # 是否置顶
    created_at = Column(DateTime, default=datetime.utcnow)

    couple = relationship("Couple", back_populates="wishes")
