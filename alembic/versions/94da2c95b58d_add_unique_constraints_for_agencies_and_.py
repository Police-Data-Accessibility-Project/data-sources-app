"""Add unique constraints for agencies and data sources

Revision ID: 94da2c95b58d
Revises: 8ba99f12446d
Create Date: 2025-02-06 19:16:55.463964

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "94da2c95b58d"
down_revision: Union[str, None] = "8ba99f12446d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "agencies_unique",
        table_name="agencies",
        columns=["name", "location_id", "jurisdiction_type"],
    )
    op.create_unique_constraint(
        "data_sources_unique",
        table_name="data_sources",
        columns=["source_url", "record_type_id"],
    )


def downgrade() -> None:
    op.drop_constraint("agencies_unique", table_name="agencies")
    op.drop_constraint("data_sources_unique", table_name="data_sources")
