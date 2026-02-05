"""backfill_likes_count_0

Revision ID: f6cf04b59bf0
Revises: d6f472423c1c
Create Date: 2026-02-04 17:32:26.060368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6cf04b59bf0'
down_revision: Union[str, Sequence[str], None] = 'd6f472423c1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ---------------------------
    # likes_count
    # ---------------------------
    op.execute(
        "UPDATE videos SET likes_count = 0 WHERE likes_count IS NULL"
    )

    with op.batch_alter_table("videos") as batch_op:
        batch_op.alter_column(
            "likes_count",
            existing_type=sa.Integer(),
            nullable=False,
            server_default="0",
        )

    # ---------------------------
    # comments_count
    # ---------------------------
    op.execute(
        "UPDATE videos SET comments_count = 0 WHERE comments_count IS NULL"
    )

    with op.batch_alter_table("videos") as batch_op:
        batch_op.alter_column(
            "comments_count",
            existing_type=sa.Integer(),
            nullable=False,
            server_default="0",
        )


def downgrade():
    with op.batch_alter_table("videos") as batch_op:
        batch_op.alter_column(
            "comments_count",
            existing_type=sa.Integer(),
            nullable=True,
            server_default=None,
        )

        batch_op.alter_column(
            "likes_count",
            existing_type=sa.Integer(),
            nullable=True,
            server_default=None,
        )

