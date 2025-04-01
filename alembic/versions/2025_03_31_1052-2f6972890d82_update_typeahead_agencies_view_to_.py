"""Update typeahead agencies view to filter by approval status

Revision ID: 2f6972890d82
Revises: 75d2ecaaa93f
Create Date: 2025-03-31 10:52:22.120095

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f6972890d82"
down_revision: Union[str, None] = "75d2ecaaa93f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS public.typeahead_agencies")

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS public.typeahead_agencies
        TABLESPACE pg_default
        AS
         SELECT a.id,
            a.name,
            a.jurisdiction_type,
            l.state_iso,
            l.locality_name AS municipality,
            l.county_name
           FROM agencies a
             LEFT JOIN link_agencies_locations lal ON lal.agency_id = a.id
             LEFT JOIN locations_expanded l ON lal.location_id = l.id
             WHERE a.approval_status = 'approved'
        WITH DATA;
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS public.typeahead_agencies")

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS public.typeahead_agencies
        TABLESPACE pg_default
        AS
         SELECT a.id,
            a.name,
            a.jurisdiction_type,
            l.state_iso,
            l.locality_name AS municipality,
            l.county_name
           FROM agencies a
             LEFT JOIN link_agencies_locations lal ON lal.agency_id = a.id
             LEFT JOIN locations_expanded l ON lal.location_id = l.id
        WITH DATA;
        """
    )
