from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import deps
from app.modules.couples import schemas, service

router = APIRouter()


def _check_couple_owner(db: Session, couple_id: int, user_id: int):
    """验证用户是否拥有该 couple"""
    couple = service.get_my_couple(db, owner_id=user_id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return couple


# ========== Couple ==========
@router.post("", response_model=schemas.CoupleRead, summary="创建或更新情侣档案")
def create_or_get_couple(
    payload: schemas.CoupleCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.create_couple(db, owner_id=current_user.id, payload=payload)


@router.get("/me", response_model=schemas.CoupleRead | None, summary="获取我的情侣档案")
def get_my_couple(
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.get_my_couple(db, owner_id=current_user.id)


# ========== Note ==========
@router.post("/{couple_id}/notes", response_model=schemas.NoteRead, summary="添加记录")
def add_note(
    couple_id: int,
    payload: schemas.NoteCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.add_note(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/notes", response_model=list[schemas.NoteRead], summary="获取记录列表")
def list_notes(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.list_notes(db, couple_id=couple_id)


@router.patch("/{couple_id}/notes/{note_id}", response_model=schemas.NoteRead, summary="更新记录")
def update_note(
    couple_id: int,
    note_id: int,
    payload: schemas.NoteCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.update_note(db, couple_id=couple_id, note_id=note_id, payload=payload)


@router.delete("/{couple_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除记录")
def delete_note(
    couple_id: int,
    note_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    service.delete_note(db, couple_id=couple_id, note_id=note_id)


# ========== Message (留言板) ==========
@router.post("/{couple_id}/messages", response_model=schemas.MessageRead, summary="添加留言")
def add_message(
    couple_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.add_message(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/messages", response_model=list[schemas.MessageRead], summary="获取留言列表")
def list_messages(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.list_messages(db, couple_id=couple_id)


@router.delete("/{couple_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除留言")
def delete_message(
    couple_id: int,
    message_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    service.delete_message(db, couple_id=couple_id, message_id=message_id)


# ========== Countdown (倒计时) ==========
@router.post("/{couple_id}/countdowns", response_model=schemas.CountdownRead, summary="添加倒计时")
def add_countdown(
    couple_id: int,
    payload: schemas.CountdownCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.add_countdown(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/countdowns", response_model=list[schemas.CountdownRead], summary="获取倒计时列表")
def list_countdowns(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.list_countdowns(db, couple_id=couple_id)


@router.patch("/{couple_id}/countdowns/{countdown_id}", response_model=schemas.CountdownRead, summary="更新倒计时")
def update_countdown(
    couple_id: int,
    countdown_id: int,
    payload: schemas.CountdownUpdate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.update_countdown(db, couple_id=couple_id, countdown_id=countdown_id, payload=payload)


@router.delete("/{couple_id}/countdowns/{countdown_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除倒计时")
def delete_countdown(
    couple_id: int,
    countdown_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    service.delete_countdown(db, couple_id=couple_id, countdown_id=countdown_id)


# ========== Wish (愿望清单) ==========
@router.post("/{couple_id}/wishes", response_model=schemas.WishRead, summary="添加愿望")
def add_wish(
    couple_id: int,
    payload: schemas.WishCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.add_wish(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/wishes", response_model=list[schemas.WishRead], summary="获取愿望列表")
def list_wishes(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.list_wishes(db, couple_id=couple_id)


@router.patch("/{couple_id}/wishes/{wish_id}", response_model=schemas.WishRead, summary="更新愿望")
def update_wish(
    couple_id: int,
    wish_id: int,
    payload: schemas.WishUpdate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    return service.update_wish(db, couple_id=couple_id, wish_id=wish_id, payload=payload)


@router.delete("/{couple_id}/wishes/{wish_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除愿望")
def delete_wish(
    couple_id: int,
    wish_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    _check_couple_owner(db, couple_id, current_user.id)
    service.delete_wish(db, couple_id=couple_id, wish_id=wish_id)
