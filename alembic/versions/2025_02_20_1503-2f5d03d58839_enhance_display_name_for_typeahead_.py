"""Enhance display name for typeahead locations materialized view

Revision ID: 2f5d03d58839
Revises: 0d1f14861bb6
Create Date: 2025-02-20 15:03:32.900346

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f5d03d58839"
down_revision: Union[str, None] = "0d1f14861bb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old materialized view
    op.execute("DROP MATERIALIZED VIEW IF EXISTS public.typeahead_locations")

    # Create new materialized view
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS public.typeahead_locations as
         SELECT le.id AS location_id,
            CASE
                WHEN le.type = 'Locality'::location_type THEN le.locality_name
                WHEN le.type = 'County'::location_type THEN le.county_name::character varying
                WHEN le.type = 'State'::location_type THEN le.state_name::character varying
                ELSE NULL::character varying
            END AS search_name,
            CASE
                WHEN le.type = 'Locality'::location_type THEN CONCAT(le.locality_name, ', ', le.county_name, ', ', le.state_name)
                WHEN le.type = 'County'::location_type THEN CONCAT(le.county_name, ', ', le.state_name)
                WHEN le.type = 'State'::location_type THEN le.state_name::character varying
                ELSE NULL::character varying
            END AS display_name,
        le.type,
        le.state_name,
        le.county_name,
        le.locality_name
       FROM locations_expanded le
    WITH DATA;
    """
    )


def downgrade() -> None:
    # Drop new materialized view
    op.execute("DROP MATERIALIZED VIEW IF EXISTS public.typeahead_locations")

    # Create old materialized view
    op.execute(
        """
    CREATE MATERIALIZED VIEW IF NOT EXISTS public.typeahead_locations
    AS
     SELECT locations_expanded.id AS location_id,
            CASE
                WHEN locations_expanded.type = 'Locality'::location_type THEN locations_expanded.locality_name
                WHEN locations_expanded.type = 'County'::location_type THEN locations_expanded.county_name::character varying
                WHEN locations_expanded.type = 'State'::location_type THEN locations_expanded.state_name::character varying
                ELSE NULL::character varying
            END AS display_name,
        locations_expanded.type,
        locations_expanded.state_name,
        locations_expanded.county_name,
        locations_expanded.locality_name
       FROM locations_expanded
    WITH DATA;
    """
    )
