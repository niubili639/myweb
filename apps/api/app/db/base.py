from sqlalchemy.orm import declarative_base

Base = declarative_base()


def import_models() -> None:
    """
    Import ORM models so Alembic can discover metadata.
    Keep imports inside to avoid circular dependencies at runtime.
    """
    from app.modules.spaces.models import SimpleKV, ChatSession, ChatMessage  # noqa: F401
    from app.modules.auth.models import User, ApiKey  # noqa: F401
    from app.modules.couples.models import Couple, CoupleNote  # noqa: F401
    from app.modules.media.models import Photo  # noqa: F401
