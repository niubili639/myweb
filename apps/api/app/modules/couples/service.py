from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.couples import schemas
from app.modules.couples.models import Couple, CoupleNote


def get_my_couple(db: Session, owner_id: int) -> Couple | None:
    return db.query(Couple).filter(Couple.owner_id == owner_id).first()


def create_couple(db: Session, owner_id: int, payload: schemas.CoupleCreate) -> Couple:
    existing = get_my_couple(db, owner_id)
    if existing:
        # update existing couple with new info
        existing.name = payload.name
        existing.start_date = payload.start_date
        existing.partner_a_name = payload.partner_a_name
        existing.partner_b_name = payload.partner_b_name
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    couple = Couple(
        name=payload.name,
        start_date=payload.start_date,
        partner_a_name=payload.partner_a_name,
        partner_b_name=payload.partner_b_name,
        owner_id=owner_id,
    )
    db.add(couple)
    db.commit()
    db.refresh(couple)
    return couple


def add_note(db: Session, couple_id: int, payload: schemas.NoteCreate) -> CoupleNote:
    couple = db.query(Couple).filter(Couple.id == couple_id).first()
    if not couple:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couple not found")
    note = CoupleNote(couple_id=couple_id, title=payload.title, content_md=payload.content_md)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(db: Session, couple_id: int):
    return (
        db.query(CoupleNote)
        .filter(CoupleNote.couple_id == couple_id)
        .order_by(CoupleNote.created_at.desc())
        .all()
    )


def update_note(db: Session, couple_id: int, note_id: int, payload: schemas.NoteCreate) -> CoupleNote:
    note = (
        db.query(CoupleNote)
        .filter(CoupleNote.couple_id == couple_id, CoupleNote.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    note.title = payload.title
    note.content_md = payload.content_md
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, couple_id: int, note_id: int) -> None:
    note = (
        db.query(CoupleNote)
        .filter(CoupleNote.couple_id == couple_id, CoupleNote.id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(note)
    db.commit()
