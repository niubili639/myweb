"""add partner names to couples"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_couple_partner_names"
down_revision = "0004_add_is_pinned"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("couples") as batch_op:
        batch_op.add_column(sa.Column("partner_a_name", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("partner_b_name", sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table("couples") as batch_op:
        batch_op.drop_column("partner_a_name")
        batch_op.drop_column("partner_b_name")
