from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import deps
from app.modules.couples import service as couple_service
from app.modules.media import schemas, service

router = APIRouter()


# ========== 新接口：按空间类型管理照片 ==========

@router.post("/photos", response_model=schemas.PhotoRead, summary="上传照片（存储URL）")
def create_photo(
    payload: schemas.PhotoCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    """上传照片到指定空间"""
    return service.add_photo(db, owner_id=current_user.id, payload=payload)


@router.get("/photos", response_model=list[schemas.PhotoRead], summary="获取照片列表")
def get_photos(
    space_type: str = "couple",
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    """获取指定空间的照片列表"""
    return service.list_photos(db, owner_id=current_user.id, space_type=space_type)


@router.delete("/photos/{photo_id}", summary="删除照片")
def remove_photo(
    photo_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    """删除照片"""
    success = service.delete_photo(db, photo_id=photo_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return {"message": "Photo deleted"}


# ========== 旧接口：兼容 couple_id 方式 ==========

@router.post("/{couple_id}/photos", response_model=schemas.PhotoRead, summary="Add photo by URL (legacy)")
def add_photo_legacy(
    couple_id: int,
    payload: schemas.PhotoCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = couple_service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.add_photo_legacy(db, couple_id=couple_id, payload=payload)


@router.get("/{couple_id}/photos", response_model=list[schemas.PhotoRead], summary="List photos (legacy)")
def list_photos_legacy(
    couple_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    couple = couple_service.get_my_couple(db, owner_id=current_user.id)
    if not couple or couple.id != couple_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your couple")
    return service.list_photos_legacy(db, couple_id=couple_id)
