from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import deps
from app.modules.couples import schemas, service

router = APIRouter()


@router.post("", response_model=schemas.CoupleRead, summary="Create or fetch my couple")
def create_or_get_couple(
    payload: schemas.CoupleCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.create_couple(db, owner_id=current_user.id, payload=payload)


@router.get("/me", response_model=schemas.CoupleRead | None, summary="Get my couple info")
def get_my_couple(
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.get_my_couple(db, owner_id=current_user.id)


@router.post("/{couple_id}/notes", response_model=schemas.NoteRead, summary="Add markdown note")
def add_note(
    couple_id: int,
    payload: schemas.NoteCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    # Ensure user owns the couple
    couple = service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.add_note(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/notes", response_model=list[schemas.NoteRead], summary="List notes")
def list_notes(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.list_notes(db, couple_id=couple_id)


@router.patch("/{couple_id}/notes/{note_id}", response_model=schemas.NoteRead, summary="Update note")
def update_note(
    couple_id: int,
    note_id: int,
    payload: schemas.NoteCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.update_note(db, couple_id=couple_id, note_id=note_id, payload=payload)


@router.delete("/{couple_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete note")
def delete_note(
    couple_id: int,
    note_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    service.delete_note(db, couple_id=couple_id, note_id=note_id)
    return None
