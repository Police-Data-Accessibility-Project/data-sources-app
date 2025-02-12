"""Change permissions permission_id to id

Revision ID: 0d9b984683a5
Revises: 61978d612820
Create Date: 2025-02-12 17:54:45.383133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d9b984683a5"
down_revision: Union[str, None] = "61978d612820"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name="permissions", column_name="permission_id", new_column_name="id"
    )


def downgrade() -> None:
    op.alter_column(
        table_name="permissions", column_name="id", new_column_name="permission_id"
    )
