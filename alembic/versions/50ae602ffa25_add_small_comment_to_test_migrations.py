"""Add small comment to test migrations

Revision ID: 50ae602ffa25
Revises: 34f45aad081a
Create Date: 2025-01-23 13:08:08.812977

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "50ae602ffa25"
down_revision: Union[str, None] = "34f45aad081a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add comment to test table
    op.create_table_comment(
        table_name="search_queue",
        comment="A queue for information about search batches which are to be sent to subscribers.",
    )


def downgrade() -> None:
    op.drop_table_comment("search_queue")
