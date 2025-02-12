"""make_agency_type_non_null

Revision ID: 83090d813802
Revises: 94da2c95b58d
Create Date: 2025-02-11 10:05:49.486152

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "83090d813802"
down_revision: Union[str, None] = "94da2c95b58d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add non-null constraint to agency_type
    op.alter_column("agencies", "agency_type", nullable=False)


def downgrade() -> None:
    # Remove non-null constraint from agency_type
    op.alter_column("agencies", "agency_type", nullable=True)
