"""Increase data request title character length to 255

Revision ID: 7b0b4eaa9764
Revises: 60e9d755ef82
Create Date: 2025-05-09 15:43:22.867333

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b0b4eaa9764"
down_revision: Union[str, None] = "60e9d755ef82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_CONSTRAINT_NAME = "title_limit"
NEW_CONSTRAINT_NAME = "data_request_title_limit"


def upgrade() -> None:
    op.drop_constraint(OLD_CONSTRAINT_NAME, table_name="data_requests", type_="check")

    op.create_check_constraint(
        NEW_CONSTRAINT_NAME,
        "data_requests",
        "length(title) <= 255",
    )


def downgrade() -> None:
    op.drop_constraint(NEW_CONSTRAINT_NAME, table_name="data_requests", type_="check")

    op.create_check_constraint(
        OLD_CONSTRAINT_NAME,
        "data_requests",
        "length(title) <= 51",
    )
