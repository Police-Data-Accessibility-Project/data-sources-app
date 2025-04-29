"""Add full display name to LocationsExpanded

Revision ID: 682dbaf958b3
Revises: 30c3f217d58d
Create Date: 2025-04-29 12:35:24.290116

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "682dbaf958b3"
down_revision: Union[str, None] = "30c3f217d58d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE VIEW public.locations_expanded
     AS
     SELECT locations.id,
        locations.type,
        us_states.state_name,
        us_states.state_iso,
        counties.name AS county_name,
        counties.fips AS county_fips,
        localities.name AS locality_name,
        localities.id AS locality_id,
        us_states.id AS state_id,
        counties.id AS county_id,
            CASE
                WHEN locations.type = 'Locality'::location_type THEN localities.name
                WHEN locations.type = 'County'::location_type THEN counties.name::character varying
                WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
                ELSE NULL::character varying
            END AS display_name,
            CASE
                WHEN locations.type = 'Locality'::location_type THEN concat(localities.name, ', ', counties.name, ', ', us_states.state_name)::character varying
                WHEN locations.type = 'County'::location_type THEN concat(counties.name, ', ', us_states.state_name)::character varying
                WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
                ELSE NULL::character varying
            END AS full_display_name
       FROM locations
         LEFT JOIN us_states ON locations.state_id = us_states.id
         LEFT JOIN counties ON locations.county_id = counties.id
         LEFT JOIN localities ON locations.locality_id = localities.id;
    """
    )


def downgrade() -> None:
    # This cannot be reversed without dropping several other views, so do nothing
    pass
