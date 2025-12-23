"""add is_pinned column to chat_sessions"""

from alembic import op
import sqlalchemy as sa


revision = "0004_add_is_pinned"
down_revision = "0003_chat_history"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("chat_sessions") as batch_op:
        batch_op.add_column(
            sa.Column("is_pinned", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade():
    with op.batch_alter_table("chat_sessions") as batch_op:
        batch_op.drop_column("is_pinned")
