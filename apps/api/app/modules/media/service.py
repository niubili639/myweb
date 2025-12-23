from sqlalchemy.orm import Session

from app.modules.media import schemas
from app.modules.media.models import Photo


def add_photo(db: Session, couple_id: int, payload: schemas.PhotoCreate) -> Photo:
    photo = Photo(couple_id=couple_id, url=payload.url, caption=payload.caption)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_photos(db: Session, couple_id: int):
    return (
        db.query(Photo)
        .filter(Photo.couple_id == couple_id)
        .order_by(Photo.created_at.desc())
        .all()
    )
