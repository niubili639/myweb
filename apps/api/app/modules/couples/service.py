from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.couples import schemas
from app.modules.couples.models import Couple, CoupleNote, CoupleMessage, CoupleCountdown, CoupleWish


# ========== Couple ==========
def get_my_couple(db: Session, owner_id: int) -> Couple | None:
    return db.query(Couple).filter(Couple.owner_id == owner_id).first()


def create_couple(db: Session, owner_id: int, payload: schemas.CoupleCreate) -> Couple:
    existing = get_my_couple(db, owner_id)
    if existing:
        existing.name = payload.name
        existing.start_date = payload.start_date
        existing.partner_a_name = payload.partner_a_name
        existing.partner_b_name = payload.partner_b_name
        if payload.partner_a_avatar is not None:
            existing.partner_a_avatar = payload.partner_a_avatar
        if payload.partner_b_avatar is not None:
            existing.partner_b_avatar = payload.partner_b_avatar
        if payload.partner_a_birthday is not None:
            existing.partner_a_birthday = payload.partner_a_birthday
        if payload.partner_b_birthday is not None:
            existing.partner_b_birthday = payload.partner_b_birthday
        if payload.partner_a_location is not None:
            existing.partner_a_location = payload.partner_a_location
        if payload.partner_b_location is not None:
            existing.partner_b_location = payload.partner_b_location
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    couple = Couple(
        name=payload.name,
        start_date=payload.start_date,
        partner_a_name=payload.partner_a_name,
        partner_b_name=payload.partner_b_name,
        partner_a_avatar=payload.partner_a_avatar,
        partner_b_avatar=payload.partner_b_avatar,
        partner_a_birthday=payload.partner_a_birthday,
        partner_b_birthday=payload.partner_b_birthday,
        partner_a_location=payload.partner_a_location,
        partner_b_location=payload.partner_b_location,
        owner_id=owner_id,
    )
    db.add(couple)
    db.commit()
    db.refresh(couple)
    return couple


# ========== Note ==========
def add_note(db: Session, couple_id: int, payload: schemas.NoteCreate) -> CoupleNote:
    note = CoupleNote(couple_id=couple_id, title=payload.title, content_md=payload.content_md)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(db: Session, couple_id: int):
    return db.query(CoupleNote).filter(CoupleNote.couple_id == couple_id).order_by(CoupleNote.created_at.desc()).all()


def update_note(db: Session, couple_id: int, note_id: int, payload: schemas.NoteCreate) -> CoupleNote:
    note = db.query(CoupleNote).filter(CoupleNote.couple_id == couple_id, CoupleNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    note.title = payload.title
    note.content_md = payload.content_md
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, couple_id: int, note_id: int) -> None:
    note = db.query(CoupleNote).filter(CoupleNote.couple_id == couple_id, CoupleNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(note)
    db.commit()


# ========== Message (留言板) ==========
def add_message(db: Session, couple_id: int, payload: schemas.MessageCreate) -> CoupleMessage:
    msg = CoupleMessage(couple_id=couple_id, author=payload.author, content=payload.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def list_messages(db: Session, couple_id: int):
    return db.query(CoupleMessage).filter(CoupleMessage.couple_id == couple_id).order_by(CoupleMessage.created_at.desc()).all()


def delete_message(db: Session, couple_id: int, message_id: int) -> None:
    msg = db.query(CoupleMessage).filter(CoupleMessage.couple_id == couple_id, CoupleMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(msg)
    db.commit()


# ========== Countdown (倒计时) ==========
def add_countdown(db: Session, couple_id: int, payload: schemas.CountdownCreate) -> CoupleCountdown:
    cd = CoupleCountdown(couple_id=couple_id, title=payload.title, target_date=payload.target_date, is_yearly=payload.is_yearly)
    db.add(cd)
    db.commit()
    db.refresh(cd)
    return cd


def list_countdowns(db: Session, couple_id: int):
    return db.query(CoupleCountdown).filter(CoupleCountdown.couple_id == couple_id).order_by(CoupleCountdown.is_pinned.desc(), CoupleCountdown.target_date).all()


def update_countdown(db: Session, couple_id: int, countdown_id: int, payload: schemas.CountdownUpdate) -> CoupleCountdown:
    cd = db.query(CoupleCountdown).filter(CoupleCountdown.couple_id == couple_id, CoupleCountdown.id == countdown_id).first()
    if not cd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Countdown not found")
    if payload.title is not None:
        cd.title = payload.title
    if payload.target_date is not None:
        cd.target_date = payload.target_date
    if payload.is_yearly is not None:
        cd.is_yearly = payload.is_yearly
    if payload.is_pinned is not None:
        cd.is_pinned = payload.is_pinned
    db.commit()
    db.refresh(cd)
    return cd


def delete_countdown(db: Session, couple_id: int, countdown_id: int) -> None:
    cd = db.query(CoupleCountdown).filter(CoupleCountdown.couple_id == couple_id, CoupleCountdown.id == countdown_id).first()
    if not cd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Countdown not found")
    db.delete(cd)
    db.commit()


# ========== Wish (愿望清单) ==========
def add_wish(db: Session, couple_id: int, payload: schemas.WishCreate) -> CoupleWish:
    wish = CoupleWish(couple_id=couple_id, title=payload.title, progress=payload.progress)
    db.add(wish)
    db.commit()
    db.refresh(wish)
    return wish


def list_wishes(db: Session, couple_id: int):
    return db.query(CoupleWish).filter(CoupleWish.couple_id == couple_id).order_by(CoupleWish.is_pinned.desc(), CoupleWish.created_at.desc()).all()


def update_wish(db: Session, couple_id: int, wish_id: int, payload: schemas.WishUpdate) -> CoupleWish:
    wish = db.query(CoupleWish).filter(CoupleWish.couple_id == couple_id, CoupleWish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found")
    if payload.title is not None:
        wish.title = payload.title
    if payload.progress is not None:
        wish.progress = payload.progress
    if payload.completed is not None:
        wish.completed = payload.completed
    if payload.is_pinned is not None:
        wish.is_pinned = payload.is_pinned
    db.commit()
    db.refresh(wish)
    return wish


def delete_wish(db: Session, couple_id: int, wish_id: int) -> None:
    wish = db.query(CoupleWish).filter(CoupleWish.couple_id == couple_id, CoupleWish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found")
    db.delete(wish)
    db.commit()
