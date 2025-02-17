"""Add unique constraint for county name and state

Revision ID: 0d1f14861bb6
Revises: 2fbf7e4d2ccf
Create Date: 2025-02-15 16:06:46.492507

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d1f14861bb6"
down_revision: Union[str, None] = "2fbf7e4d2ccf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "unique_county_name_and_state", "counties", ["name", "state_id"]
    )
    op.drop_column(table_name="counties", column_name="state_iso")


def downgrade() -> None:
    op.add_column(
        table_name="counties",
        column=sa.Column(
            "state_iso", sa.VARCHAR(length=2), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint("unique_county_name_and_state", "counties", type_="unique")
