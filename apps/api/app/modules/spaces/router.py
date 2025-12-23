from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import deps
from app.modules.spaces import schemas, service

router = APIRouter()


@router.post("/ai/chat", response_model=schemas.ChatResponse, summary="Qwen chat")
async def chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    reply, session_id = await service.chat_and_store(db, user_id=current_user.id, payload=payload)
    return schemas.ChatResponse(reply=reply, session_id=session_id)


@router.post("/ai/image", response_model=schemas.ImageResponse, summary="Qwen image generation")
async def image(
    payload: schemas.ImageRequest,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    urls, session_id = await service.image_and_store(db, user_id=current_user.id, payload=payload)
    return schemas.ImageResponse(images=urls, session_id=session_id)


@router.get("/sessions", response_model=list[schemas.ChatSessionRead], summary="List chat sessions")
async def list_chat_sessions(
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.list_sessions(db, user_id=current_user.id)


@router.post("/sessions", response_model=schemas.ChatSessionRead, summary="Create chat session")
async def create_chat_session(
    payload: schemas.ChatSessionCreate,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    session = service._ensure_session(
        db,
        user_id=current_user.id,
        session_id=None,
        mode=payload.mode,
        model=payload.model,
        title=payload.title,
    )
    return session


@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[schemas.ChatMessageRead],
    summary="List messages in a session",
)
async def list_chat_messages(
    session_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.list_messages(db, user_id=current_user.id, session_id=session_id)


@router.post("/sessions/{session_id}/pin", response_model=schemas.ChatSessionRead, summary="Pin/Unpin session")
async def pin_chat_session(
    session_id: int,
    is_pinned: bool,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    return service.set_session_pin(db, user_id=current_user.id, session_id=session_id, is_pinned=is_pinned)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete session")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(deps.get_db_session),
    current_user=Depends(deps.get_current_active_user),
):
    service.delete_session(db, user_id=current_user.id, session_id=session_id)
    return None
