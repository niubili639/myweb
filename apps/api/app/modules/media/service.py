from sqlalchemy.orm import Session

from app.modules.media import schemas
from app.modules.media.models import Photo


def add_photo(db: Session, owner_id: int, payload: schemas.PhotoCreate) -> Photo:
    photo = Photo(
        owner_id=owner_id,
        url=payload.url,
        thumbnail_url=payload.thumbnail_url,
        caption=payload.caption,
        image_key=payload.image_key,
        space_type=payload.space_type,
        space_id=payload.space_id,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_photos(db: Session, owner_id: int, space_type: str = "couple"):
    return (
        db.query(Photo)
        .filter(Photo.owner_id == owner_id, Photo.space_type == space_type)
        .order_by(Photo.created_at.desc())
        .all()
    )


def get_photo(db: Session, photo_id: int, owner_id: int) -> Photo | None:
    return (
        db.query(Photo)
        .filter(Photo.id == photo_id, Photo.owner_id == owner_id)
        .first()
    )


def delete_photo(db: Session, photo_id: int, owner_id: int) -> bool:
    photo = get_photo(db, photo_id, owner_id)
    if not photo:
        return False
    db.delete(photo)
    db.commit()
    return True


# 兼容旧接口
def add_photo_legacy(db: Session, couple_id: int, payload) -> Photo:
    photo = Photo(couple_id=couple_id, url=payload.url, caption=payload.caption)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_photos_legacy(db: Session, couple_id: int):
    return (
        db.query(Photo)
        .filter(Photo.couple_id == couple_id)
        .order_by(Photo.created_at.desc())
        .all()
    )
