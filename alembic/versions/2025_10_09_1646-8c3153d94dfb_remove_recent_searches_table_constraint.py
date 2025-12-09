"""Remove recent searches table constraint

Revision ID: 8c3153d94dfb
Revises: 2f8bd4749166
Create Date: 2025-10-09 16:46:49.858892

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8c3153d94dfb"
down_revision: Union[str, None] = "2f8bd4749166"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "recent_searches",
        column_name="location_id",
        nullable=True,
    )


def downgrade() -> None:
    pass
