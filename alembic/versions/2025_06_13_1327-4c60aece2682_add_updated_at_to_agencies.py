"""Add updated_at to agencies

Revision ID: 4c60aece2682
Revises: 276dd2752d44
Create Date: 2025-06-13 13:27:39.750600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import updated_at_column

# revision identifiers, used by Alembic.
revision: str = '4c60aece2682'
down_revision: Union[str, None] = '276dd2752d44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'agencies',
        updated_at_column()
    )


def downgrade() -> None:
    op.drop_column('agencies', 'updated_at')
