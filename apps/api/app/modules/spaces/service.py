import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import logger
from app.modules.auth import service as auth_service
from app.modules.spaces import schemas
from app.modules.spaces.models import ChatSession, ChatMessage

settings = get_settings()


def _get_qwen_api_key(db: Session) -> str:
    api_key = auth_service.get_api_key(db, provider="qwen")
    if api_key:
        return api_key.key
    if settings.qwen_api_key:
        return settings.qwen_api_key
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Qwen API key not configured")


async def chat_with_qwen(db: Session, payload: schemas.ChatRequest) -> str:
    api_key = _get_qwen_api_key(db)
    url = f"{settings.qwen_base_url}/services/aigc/text-generation/generation"
    messages = payload.history or []
    messages.append({"role": "user", "content": payload.prompt})
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    model = payload.model or settings.qwen_model
    body = {"model": model, "input": {"messages": messages}}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=body)
    logger.info(f"Qwen chat resp status={resp.status_code}")
    logger.info(f"Qwen chat resp body={resp.text}")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail={"error": "qwen_error", "body": resp.text})
    data = resp.json()
    try:
        # dashscope 文本模型可能返回 output.text 或 output.choices[*].message.content
        if "text" in data.get("output", {}):
            return data["output"]["text"]
        return data["output"]["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "invalid_qwen_response", "body": resp.text},
        )


async def generate_image(db: Session, payload: schemas.ImageRequest) -> list[str]:
    api_key = _get_qwen_api_key(db)
    # Sync multimodal generation (recommended in dashscope docs)
    url = f"{settings.qwen_base_url}/services/aigc/multimodal-generation/generation"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    model = payload.model or settings.qwen_image_model
    # Qwen image only accepts specific sizes; fallback if input不合法
    allowed_sizes = {
        "1664*928",
        "1472*1140",
        "1328*1328",
        "1140*1472",
        "928*1664",
    }
    size = payload.size or "1328*1328"
    if size not in allowed_sizes:
        size = "1328*1328"
    body = {
        "model": model,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": payload.prompt},
                    ],
                }
            ]
        },
        "parameters": {
            "size": size,
            "prompt_extend": True,
            "watermark": False,
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=body)
    logger.info(f"Qwen image resp status={resp.status_code}")
    logger.info(f"Qwen image resp body={resp.text}")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail={"error": "qwen_error", "body": resp.text})
    data = resp.json()
    try:
        choices = data["output"]["choices"]
        urls = []
        for choice in choices:
            contents = choice.get("message", {}).get("content", [])
            for item in contents:
                if "image" in item:
                    urls.append(item["image"])
        if not urls:
            raise KeyError("no_image")
        return urls
    except (KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "invalid_qwen_response", "body": resp.text},
        )


def _ensure_session(db: Session, user_id: int, session_id: int | None, mode: str, model: str | None, title: str | None = None) -> ChatSession:
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return session
    session = ChatSession(user_id=user_id, mode=mode, model=model, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, user_id: int):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.is_pinned.desc(), ChatSession.created_at.desc())
        .all()
    )


def list_messages(db: Session, user_id: int, session_id: int):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def set_session_pin(db: Session, user_id: int, session_id: int, is_pinned: bool) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    session.is_pinned = 1 if is_pinned else 0
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, user_id: int, session_id: int) -> None:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    db.delete(session)
    db.commit()


async def chat_and_store(db: Session, user_id: int, payload: schemas.ChatRequest) -> tuple[str, int]:
    session = _ensure_session(
        db,
        user_id=user_id,
        session_id=payload.session_id,
        mode="chat",
        model=payload.model or settings.qwen_model,
        title=payload.prompt[:60],
    )
    # store user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=payload.prompt, message_type="text")
    db.add(user_msg)
    db.commit()

    # build history from DB
    history_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history = [{"role": row.role, "content": row.content} for row in history_rows if row.message_type == "text"]
    payload.history = history
    reply = await chat_with_qwen(db, payload)
    assistant_msg = ChatMessage(session_id=session.id, role="assistant", content=reply, message_type="text")
    db.add(assistant_msg)
    db.commit()
    return reply, session.id


async def image_and_store(db: Session, user_id: int, payload: schemas.ImageRequest) -> tuple[list[str], int]:
    session = _ensure_session(
        db,
        user_id=user_id,
        session_id=payload.session_id,
        mode="image",
        model=payload.model or settings.qwen_image_model,
        title=payload.prompt[:60],
    )
    user_msg = ChatMessage(session_id=session.id, role="user", content=payload.prompt, message_type="text")
    db.add(user_msg)
    db.commit()

    urls = await generate_image(db, payload)
    assistant_msg = ChatMessage(
        session_id=session.id, role="assistant", content="\n".join(urls), message_type="image"
    )
    db.add(assistant_msg)
    db.commit()
    return urls, session.id
