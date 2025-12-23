"""add chat sessions and messages

Revision ID: 0003_chat_history
Revises: 0002_add_role_spaces_invite
Create Date: 2025-12-22
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_chat_history"
down_revision = "0002_add_role_spaces_invite"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "chat_sessions" not in tables:
        op.create_table(
            "chat_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
            sa.Column("title", sa.String(length=200), nullable=True),
            sa.Column("mode", sa.String(length=20), nullable=False, server_default="chat"),
            sa.Column("model", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
    indexes = {idx["name"] for idx in inspector.get_indexes("chat_sessions")} if "chat_sessions" in tables else set()
    if "ix_chat_sessions_user_id" not in indexes and "chat_sessions" in tables:
        op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    if "chat_messages" not in tables:
        op.create_table(
            "chat_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("session_id", sa.Integer(), sa.ForeignKey("chat_sessions.id"), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("message_type", sa.String(length=20), nullable=False, server_default="text"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
    msg_indexes = {idx["name"] for idx in inspector.get_indexes("chat_messages")} if "chat_messages" in tables else set()
    if "ix_chat_messages_session_id" not in msg_indexes and "chat_messages" in tables:
        op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_sessions_user_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")
