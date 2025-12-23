from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    caption = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    couple = relationship("Couple", back_populates="photos")
