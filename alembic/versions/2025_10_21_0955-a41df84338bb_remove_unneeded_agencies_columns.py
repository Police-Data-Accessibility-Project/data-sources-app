"""Remove unneeded agencies columns

Revision ID: a41df84338bb
Revises: e51211c51b29
Create Date: 2025-10-21 09:55:20.961243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a41df84338bb'
down_revision: Union[str, None] = 'e51211c51b29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AGENCIES_TABLE_NAME: str = "agencies"

def upgrade() -> None:
    op.alter_column(
        table_name=AGENCIES_TABLE_NAME,
        column_name="agency_created",
        new_column_name="created_at",
    )
    op.drop_column(AGENCIES_TABLE_NAME, "multi_agency")
    op.drop_column(AGENCIES_TABLE_NAME, "airtable_agency_last_modified")
    op.drop_column(AGENCIES_TABLE_NAME, "airtable_uid")


def downgrade() -> None:
    pass
