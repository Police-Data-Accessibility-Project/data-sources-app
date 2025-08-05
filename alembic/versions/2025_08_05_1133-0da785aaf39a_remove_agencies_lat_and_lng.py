"""Remove agencies lat and lng

Revision ID: 0da785aaf39a
Revises: 0896cefcf910
Create Date: 2025-08-05 11:33:49.811218

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0da785aaf39a"
down_revision: Union[str, None] = "0896cefcf910"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("agencies", "lat")
    op.drop_column("agencies", "lng")


def downgrade() -> None:
    op.add_column("agencies", sa.Column("lat", sa.Float(), nullable=True))
    op.add_column("agencies", sa.Column("lng", sa.Float(), nullable=True))
