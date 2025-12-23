from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import deps
from app.modules.couples import service as couple_service
from app.modules.media import schemas, service

router = APIRouter()


@router.post("/{couple_id}/photos", response_model=schemas.PhotoRead, summary="Add photo by URL")
def add_photo(
    couple_id: int,
    payload: schemas.PhotoCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = couple_service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.add_photo(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/photos", response_model=list[schemas.PhotoRead], summary="List photos")
def list_photos(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = couple_service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.list_photos(db, couple_id=couple_id)
