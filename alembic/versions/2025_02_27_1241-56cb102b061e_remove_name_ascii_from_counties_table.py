"""Remove name_ascii from counties table

Revision ID: 56cb102b061e
Revises: 4713a996cf91
Create Date: 2025-02-27 12:41:30.007249

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "56cb102b061e"
down_revision: Union[str, None] = "4713a996cf91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("counties", "name_ascii")


def downgrade() -> None:
    op.add_column("counties", sa.Column("name_ascii", sa.Text, nullable=True))
