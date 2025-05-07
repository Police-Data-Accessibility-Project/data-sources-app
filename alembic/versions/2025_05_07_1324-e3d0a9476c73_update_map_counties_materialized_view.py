"""Update map_counties materialized view

Revision ID: e3d0a9476c73
Revises: 8fa3633226c9
Create Date: 2025-05-07 13:24:32.013347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e3d0a9476c73"
down_revision: Union[str, None] = "8fa3633226c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_counties")
    op.execute(
        """
        CREATE MATERIALIZED VIEW map_counties AS
        WITH all_county_locations AS (
            SELECT lp.id AS county_location_id, dp.dependent_location_id
            FROM locations lp
            LEFT JOIN dependent_locations dp ON lp.id = dp.parent_location_id
            WHERE lp.type = 'County'

            UNION ALL

            -- Include self
            SELECT id AS county_location_id, id AS dependent_location_id
            FROM locations
            WHERE type = 'County'
        )
        SELECT 
            c.name AS county_name,
            s.state_iso,
            acl.county_location_id AS location_id,
            c.fips,
            COUNT(DISTINCT las.data_source_id) AS data_source_count
        FROM all_county_locations acl
        JOIN counties c ON c.id = (SELECT county_id FROM locations WHERE id = acl.county_location_id)
        JOIN us_states s ON s.id = c.state_id
        LEFT JOIN link_agencies_locations lal ON lal.location_id = acl.dependent_location_id
        LEFT JOIN link_agencies_data_sources las ON las.agency_id = lal.agency_id
        GROUP BY c.name, s.state_iso, acl.county_location_id, c.fips;
    """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_counties")
    op.execute(
        """
        CREATE MATERIALIZED VIEW map_counties AS
        WITH all_county_locations AS (
            SELECT lp.id AS county_location_id, dp.dependent_location_id
            FROM locations lp
            LEFT JOIN dependent_locations dp ON lp.id = dp.parent_location_id
            WHERE lp.type = 'County'

            UNION ALL

            -- Include self
            SELECT id AS county_location_id, id AS dependent_location_id
            FROM locations
            WHERE type = 'County'
        )
        SELECT 
            c.name AS county_name,
            s.state_iso,
            acl.county_location_id AS location_id,
            COUNT(DISTINCT las.data_source_id) AS data_source_count
        FROM all_county_locations acl
        JOIN counties c ON c.id = (SELECT county_id FROM locations WHERE id = acl.county_location_id)
        JOIN us_states s ON s.id = c.state_id
        LEFT JOIN link_agencies_locations lal ON lal.location_id = acl.dependent_location_id
        LEFT JOIN link_agencies_data_sources las ON las.agency_id = lal.agency_id
        GROUP BY c.name, s.state_iso, acl.county_location_id;
    """
    )
