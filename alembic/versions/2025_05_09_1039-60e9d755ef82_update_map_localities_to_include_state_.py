"""Update map_localities to include state_iso and county fips

Revision ID: 60e9d755ef82
Revises: e3d0a9476c73
Create Date: 2025-05-09 10:39:17.958207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60e9d755ef82'
down_revision: Union[str, None] = 'e3d0a9476c73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_localities")

    op.execute(
        """
    CREATE MATERIALIZED VIEW map_localities AS
    SELECT 
        loc.name AS locality_name,
        c.name AS county_name,
        l.lat,
        l.lng,
        l.id AS location_id,
        c.fips as county_fips,
        s.state_iso,
        COUNT(DISTINCT las.data_source_id) AS data_source_count
    FROM public.localities loc
    JOIN public.counties c 
        ON loc.county_id = c.id
    JOIN public.us_states s 
        ON c.state_id = s.id
    JOIN public.locations l 
        ON l.locality_id = loc.id AND l.type = 'Locality'
    LEFT JOIN public.link_agencies_locations lal 
        ON lal.location_id = l.id
    LEFT JOIN public.link_agencies_data_sources las 
        ON las.agency_id = lal.agency_id
    WHERE l.LAT IS NOT NULL AND l.LNG IS NOT NULL
    GROUP BY loc.name, c.name, l.lat, l.lng, l.id, c.fips, s.state_iso;
    """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS map_localities")

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
