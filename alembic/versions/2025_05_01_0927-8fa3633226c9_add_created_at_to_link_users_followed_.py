"""Add created_at to Link_users_followed_locations

Revision ID: 8fa3633226c9
Revises: 682dbaf958b3
Create Date: 2025-05-01 09:27:57.980239

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8fa3633226c9"
down_revision: Union[str, None] = "682dbaf958b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "link_user_followed_location",
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_column("link_user_followed_location", "created_at")
