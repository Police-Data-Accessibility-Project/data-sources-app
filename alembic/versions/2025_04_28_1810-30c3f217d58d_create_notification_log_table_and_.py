"""Create notification log table and followed searches materialized view

Revision ID: 30c3f217d58d
Revises: 787dbb5518e8
Create Date: 2025-04-28 18:10:20.638196

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "30c3f217d58d"
down_revision: Union[str, None] = "787dbb5518e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notification log table
    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column("user_count", sa.Integer, nullable=False),
    )

    # Create data sources location convenience view
    op.execute(
        """
        CREATE VIEW link_locations_data_sources_view AS
        SELECT
            L.ID LOCATION_ID,
            LAD.DATA_SOURCE_ID DATA_SOURCE_ID
        FROM
            LOCATIONS L
            INNER JOIN LINK_AGENCIES_LOCATIONS LAL ON L.ID = LAL.LOCATION_ID
            INNER JOIN LINK_AGENCIES_DATA_SOURCES LAD ON LAL.AGENCY_ID = LAD.AGENCY_ID
        """
    )


def downgrade() -> None:
    op.drop_table("notification_log")

    op.execute("DROP VIEW IF EXISTS link_locations_data_sources_view")
