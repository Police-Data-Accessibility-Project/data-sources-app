"""Create table_count_log table

Revision ID: 9b4fc9265406
Revises: dd2295f7225e
Create Date: 2025-02-13 14:11:20.816708

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b4fc9265406"
down_revision: Union[str, None] = "dd2295f7225e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "table_count_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("table_name", sa.String, nullable=False),
        sa.Column("count", sa.Integer, nullable=False),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("table_count_log")
