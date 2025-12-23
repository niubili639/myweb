"""make couple_id nullable in photos"""

from alembic import op
import sqlalchemy as sa


revision = "0007_make_couple_id_nullable"
down_revision = "0006_add_space_type_to_photos"
branch_labels = None
depends_on = None


def upgrade():
    # 修改 couple_id 允许为空
    with op.batch_alter_table("photos") as batch_op:
        batch_op.alter_column(
            "couple_id",
            existing_type=sa.Integer(),
            nullable=True
        )


def downgrade():
    with op.batch_alter_table("photos") as batch_op:
        batch_op.alter_column(
            "couple_id",
            existing_type=sa.Integer(),
            nullable=False
        )
