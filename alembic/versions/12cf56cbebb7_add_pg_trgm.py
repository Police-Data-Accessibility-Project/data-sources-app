"""Add pg_trgm

Revision ID: 12cf56cbebb7
Revises: 50ae602ffa25
Create Date: 2025-02-01 14:45:50.120436

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "12cf56cbebb7"
down_revision: Union[str, None] = "50ae602ffa25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
