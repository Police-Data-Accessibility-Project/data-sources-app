"""Add check for approval status and record_type_id

Revision ID: 9689f73c0938
Revises: 2970f0ba9eee
Create Date: 2025-07-05 14:39:10.592108

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9689f73c0938'
down_revision: Union[str, None] = '2970f0ba9eee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CONSTRAINT_NAME = 'check_for_approval_status_and_record_type_id'
TABLE_NAME = 'data_sources'

def upgrade() -> None:
    op.create_check_constraint(
        CONSTRAINT_NAME,
        TABLE_NAME,
        'approval_status != \'approved\' OR record_type_id IS NOT NULL'
    )


def downgrade() -> None:
    op.drop_constraint(
        CONSTRAINT_NAME,
        TABLE_NAME,
        type_='check'
    )
