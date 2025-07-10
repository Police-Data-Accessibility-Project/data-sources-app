"""Add user_capacities table

Revision ID: d6c5ae86c776
Revises: 9689f73c0938
Create Date: 2025-07-10 09:59:25.145652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import id_column, user_id_column, enum_column, drop_enum

# revision identifiers, used by Alembic.
revision: str = 'd6c5ae86c776'
down_revision: Union[str, None] = '9689f73c0938'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'user_capacities'
ENUM_NAME = 'user_capacities_enum'
ENUM_VALUES = [
    'advocate',
    'community_member',
    'data_publisher',
    'lawyer',
    'journalist',
    'police',
    'public_official',
    'researcher',
]

def upgrade() -> None:

    # Create table
    op.create_table(
        TABLE_NAME,
        id_column(),
        user_id_column(),
        enum_column(column_name='capacity', enum_name=ENUM_NAME, enum_values=ENUM_VALUES),
        sa.UniqueConstraint('user_id', 'capacity', name='user_capacities_user_id_capacity_key'),
    )

def downgrade() -> None:
    op.drop_table(TABLE_NAME)
    drop_enum(ENUM_NAME)
