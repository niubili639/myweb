from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    space_type = Column(String(32), nullable=False, default="couple", index=True)  # couple/family/friends
    space_id = Column(Integer, nullable=True, index=True)  # 关联的空间ID（可选）
    url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    caption = Column(String(255), nullable=True)
    image_key = Column(String(128), nullable=True)  # 图床返回的key，用于删除
    created_at = Column(DateTime, default=datetime.utcnow)

    # 保留旧的 couple_id 兼容
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=True, index=True)
    couple = relationship("Couple", back_populates="photos")
