"""add reference images to generation jobs

Revision ID: 7d90b2e6f4a1
Revises: b19a6c714dfb
Create Date: 2026-03-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d90b2e6f4a1"
down_revision: Union[str, Sequence[str], None] = "b19a6c714dfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "video_generation_jobs",
        sa.Column(
            "reference_image_paths",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )


def downgrade() -> None:
    op.drop_column("video_generation_jobs", "reference_image_paths")
