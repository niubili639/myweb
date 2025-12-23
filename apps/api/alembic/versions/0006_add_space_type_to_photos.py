"""add space_type and related fields to photos"""

from alembic import op
import sqlalchemy as sa


revision = "0006_add_space_type_to_photos"
down_revision = "0005_add_couple_partner_names"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("photos") as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("space_type", sa.String(length=32), nullable=True, server_default="couple"))
        batch_op.add_column(sa.Column("space_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("thumbnail_url", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("image_key", sa.String(length=128), nullable=True))
        batch_op.create_index("ix_photos_owner_id", ["owner_id"])
        batch_op.create_index("ix_photos_space_type", ["space_type"])
        batch_op.create_index("ix_photos_space_id", ["space_id"])


def downgrade():
    with op.batch_alter_table("photos") as batch_op:
        batch_op.drop_index("ix_photos_space_id")
        batch_op.drop_index("ix_photos_space_type")
        batch_op.drop_index("ix_photos_owner_id")
        batch_op.drop_column("image_key")
        batch_op.drop_column("thumbnail_url")
        batch_op.drop_column("space_id")
        batch_op.drop_column("space_type")
        batch_op.drop_column("owner_id")
