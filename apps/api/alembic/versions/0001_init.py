"""initial schema with users, couples, notes, photos, api_keys, simple_kv

Revision ID: 0001_init
Revises:
Create Date: 2025-12-22
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("key", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("provider", name="uq_api_keys_provider"),
    )

    op.create_table(
        "simple_kv",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=50), nullable=False, unique=True),
        sa.Column("value", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_simple_kv_id", "simple_kv", ["id"])
    op.create_index("ix_simple_kv_key", "simple_kv", ["key"], unique=True)

    op.create_table(
        "couples",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_couples_owner_id", "couples", ["owner_id"])

    op.create_table(
        "couple_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("couple_id", sa.Integer(), sa.ForeignKey("couples.id"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_couple_notes_couple_id", "couple_notes", ["couple_id"])

    op.create_table(
        "photos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("couple_id", sa.Integer(), sa.ForeignKey("couples.id"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("caption", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_photos_couple_id", "photos", ["couple_id"])


def downgrade() -> None:
    op.drop_index("ix_photos_couple_id", table_name="photos")
    op.drop_table("photos")
    op.drop_index("ix_couple_notes_couple_id", table_name="couple_notes")
    op.drop_table("couple_notes")
    op.drop_index("ix_couples_owner_id", table_name="couples")
    op.drop_table("couples")
    op.drop_index("ix_simple_kv_key", table_name="simple_kv")
    op.drop_index("ix_simple_kv_id", table_name="simple_kv")
    op.drop_table("simple_kv")
    op.drop_table("api_keys")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
