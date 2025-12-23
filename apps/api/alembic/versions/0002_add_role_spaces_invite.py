"""add role and allowed_spaces to users

Revision ID: 0002_add_role_spaces_invite
Revises: 0001_init
Create Date: 2025-12-22
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_role_spaces_invite"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("users")}

    if "role" not in columns:
        op.add_column(
            "users",
            sa.Column("role", sa.String(length=50), nullable=False, server_default="user"),
        )
    if "allowed_spaces" not in columns:
        op.add_column("users", sa.Column("allowed_spaces", sa.Text(), nullable=True))
        op.execute("UPDATE users SET allowed_spaces='couple'")
    op.execute(
        "UPDATE users SET role='admin', allowed_spaces='couple,family,friends,ai' WHERE is_admin=1"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("users")}

    if "allowed_spaces" in columns:
        op.drop_column("users", "allowed_spaces")
    if "role" in columns:
        op.drop_column("users", "role")
