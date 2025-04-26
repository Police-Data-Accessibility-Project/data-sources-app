"""Add lat and lng to locations endpoint

Revision ID: 787dbb5518e8
Revises: d7634d1796d7
Create Date: 2025-04-23 16:22:05.924511

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "787dbb5518e8"
down_revision: Union[str, None] = "d7634d1796d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "locations",
        sa.Column("lat", sa.Float, nullable=True),
    )
    op.add_column(
        "locations",
        sa.Column("lng", sa.Float, nullable=True),
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW map_states AS
        WITH all_state_locations AS (
            SELECT lp.id AS state_location_id, dp.dependent_location_id
            FROM locations lp
            LEFT JOIN dependent_locations dp ON lp.id = dp.parent_location_id
            WHERE lp.type = 'State'
            
            UNION ALL
            
            -- Include self
            SELECT id AS state_location_id, id AS dependent_location_id
            FROM locations
            WHERE type = 'State'
        )
        SELECT 
            s.state_name,
            asl.state_location_id AS location_id,
            COUNT(DISTINCT las.data_source_id) AS data_source_count
        FROM all_state_locations asl
        JOIN us_states s ON s.id = (SELECT state_id FROM locations WHERE id = asl.state_location_id)
        LEFT JOIN link_agencies_locations lal ON lal.location_id = asl.dependent_location_id
        LEFT JOIN link_agencies_data_sources las ON las.agency_id = lal.agency_id
        GROUP BY s.state_name, asl.state_location_id;

    """
    )

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

    op.execute(
        """
    CREATE MATERIALIZED VIEW map_localities AS
    SELECT 
        loc.name AS locality_name,
        c.name AS county_name,
        l.lat,
        l.lng,
        l.id AS location_id,
        COUNT(DISTINCT las.data_source_id) AS data_source_count
    FROM public.localities loc
    JOIN public.counties c 
        ON loc.county_id = c.id
    JOIN public.locations l 
        ON l.locality_id = loc.id AND l.type = 'Locality'
    LEFT JOIN public.link_agencies_locations lal 
        ON lal.location_id = l.id
    LEFT JOIN public.link_agencies_data_sources las 
        ON las.agency_id = lal.agency_id
    WHERE l.LAT IS NOT NULL AND l.LNG IS NOT NULL
    GROUP BY loc.name, c.name, l.lat, l.lng, l.id;
    """
    )

    op.execute(
        """
    CREATE MATERIALIZED VIEW total_data_sources_by_location_type AS
        WITH all_location_mappings AS (
            SELECT parent_location_id, dependent_location_id FROM dependent_locations
            UNION ALL
            SELECT id, id FROM locations
        ),
        data_sources_per_location AS (
        SELECT 
            alm.parent_location_id,
            las.data_source_id
        FROM all_location_mappings alm
        JOIN link_agencies_locations lal 
            ON lal.location_id = alm.dependent_location_id
        JOIN link_agencies_data_sources las 
            ON las.agency_id = lal.agency_id
    )
    SELECT
        COUNT(DISTINCT data_sources_per_location.data_source_id) FILTER (WHERE locations.type = 'State') AS states,
        COUNT(DISTINCT data_sources_per_location.data_source_id) FILTER (WHERE locations.type = 'County') AS counties,
        COUNT(DISTINCT data_sources_per_location.data_source_id) FILTER (WHERE locations.type = 'Locality') AS localities
    FROM data_sources_per_location
    JOIN locations ON locations.id = data_sources_per_location.parent_location_id;
    """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_states")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_counties")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_localities")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS total_data_sources_by_location_type")

    op.drop_column("locations", "lat")
    op.drop_column("locations", "lng")
