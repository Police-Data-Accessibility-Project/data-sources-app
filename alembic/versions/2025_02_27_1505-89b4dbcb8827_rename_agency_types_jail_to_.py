"""Rename agency types jail to incarceration police to law enforcement

Revision ID: 89b4dbcb8827
Revises: 203f11778425
Create Date: 2025-02-27 15:05:47.507809

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "89b4dbcb8827"
down_revision: Union[str, None] = "203f11778425"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

agency_type_enum = sa.Enum(
    "incarceration",
    "law enforcement",
    "aggregated",
    "court",
    "unknown",
    name="agency_type",
)


def upgrade() -> None:
    op.execute(
        """
    UPDATE AGENCIES
    SET agency_type = 'incarceration'
    WHERE agency_type = 'jail'
    """
    )

    op.execute(
        """
    UPDATE AGENCIES
    SET agency_type = 'law enforcement'
    WHERE agency_type = 'police'
    """
    )

    agency_type_enum.create(op.get_bind())

    op.execute("""DROP VIEW IF EXISTS agencies_expanded""")
    op.alter_column(
        "agencies",
        "agency_type",
        type_=agency_type_enum,
        postgresql_using="agency_type::agency_type",
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW public.agencies_expanded
     AS
     SELECT a.name,
        a.name AS submitted_name,
        a.homepage_url,
        a.jurisdiction_type,
        l.state_iso,
        l.state_name,
        l.county_fips,
        l.county_name,
        a.lat,
        a.lng,
        a.defunct_year,
        a.id,
        a.agency_type,
        a.multi_agency,
        a.no_web_presence,
        a.airtable_agency_last_modified,
        a.approval_status,
        a.rejection_reason,
        a.last_approval_editor,
        a.submitter_contact,
        a.agency_created,
        l.locality_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id;
        """
    )


def downgrade() -> None:
    op.execute("""DROP VIEW IF EXISTS agencies_expanded""")
    op.alter_column(
        "agencies", "agency_type", type_=sa.String, postgresql_using="agency_type::TEXT"
    )

    agency_type_enum.drop(op.get_bind())

    op.execute(
        """
    UPDATE AGENCIES
    SET agency_type = 'jail'
    WHERE agency_type = 'incarceration'
    """
    )

    op.execute(
        """
    UPDATE AGENCIES
    SET agency_type = 'police'
    WHERE agency_type = 'law enforcement'
    """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW public.agencies_expanded
     AS
     SELECT a.name,
        a.name AS submitted_name,
        a.homepage_url,
        a.jurisdiction_type,
        l.state_iso,
        l.state_name,
        l.county_fips,
        l.county_name,
        a.lat,
        a.lng,
        a.defunct_year,
        a.id,
        a.agency_type,
        a.multi_agency,
        a.no_web_presence,
        a.airtable_agency_last_modified,
        a.approval_status,
        a.rejection_reason,
        a.last_approval_editor,
        a.submitter_contact,
        a.agency_created,
        l.locality_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id;
        """
    )
