"""add couple features: avatar, birthday, messages, countdowns, wishes"""

from alembic import op
import sqlalchemy as sa


revision = "0008_add_couple_features"
down_revision = "0007_make_couple_id_nullable"
branch_labels = None
depends_on = None


def upgrade():
    # 扩展 couples 表
    with op.batch_alter_table("couples") as batch_op:
        batch_op.add_column(sa.Column("partner_a_avatar", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("partner_b_avatar", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("partner_a_birthday", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("partner_b_birthday", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("partner_a_location", sa.String(200), nullable=True))
        batch_op.add_column(sa.Column("partner_b_location", sa.String(200), nullable=True))

    # 创建留言板表
    op.create_table(
        "couple_messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("couple_id", sa.Integer(), sa.ForeignKey("couples.id"), nullable=False, index=True),
        sa.Column("author", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # 创建倒计时表
    op.create_table(
        "couple_countdowns",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("couple_id", sa.Integer(), sa.ForeignKey("couples.id"), nullable=False, index=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("is_yearly", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # 创建愿望清单表
    op.create_table(
        "couple_wishes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("couple_id", sa.Integer(), sa.ForeignKey("couples.id"), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("progress", sa.Integer(), default=0),
        sa.Column("completed", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("couple_wishes")
    op.drop_table("couple_countdowns")
    op.drop_table("couple_messages")

    with op.batch_alter_table("couples") as batch_op:
        batch_op.drop_column("partner_b_location")
        batch_op.drop_column("partner_a_location")
        batch_op.drop_column("partner_b_birthday")
        batch_op.drop_column("partner_a_birthday")
        batch_op.drop_column("partner_b_avatar")
        batch_op.drop_column("partner_a_avatar")
