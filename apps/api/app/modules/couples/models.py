from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Couple(Base):
    __tablename__ = "couples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    partner_a_name = Column(String(100), nullable=True)
    partner_b_name = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("CoupleNote", back_populates="couple", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="couple", cascade="all, delete-orphan")


class CoupleNote(Base):
    __tablename__ = "couple_notes"

    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content_md = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    couple = relationship("Couple", back_populates="notes")
