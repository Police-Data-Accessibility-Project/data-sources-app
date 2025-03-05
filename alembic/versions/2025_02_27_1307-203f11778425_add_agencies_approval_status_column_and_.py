"""Add agencies approval_status column and remove approved column

Revision ID: 203f11778425
Revises: 56cb102b061e
Create Date: 2025-02-27 13:07:47.967963

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "203f11778425"
down_revision: Union[str, None] = "56cb102b061e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


approval_status_enum = sa.Enum(
    "rejected", "approved", "needs identification", "pending", name="approval_status"
)


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS agencies_expanded")
    op.add_column(
        "agencies",
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=False,
            server_default="pending",
        ),
    )
    op.execute(
        """
        UPDATE AGENCIES
        SET approval_status = 
            CASE 
                WHEN approved = TRUE THEN 'approved'::approval_status
                ELSE 'pending'::approval_status
            END
    """
    )
    op.drop_column("agencies", "approved")
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
    op.add_column(
        "agencies",
        sa.Column("approved", sa.Boolean, nullable=False, server_default="FALSE"),
    )
    op.execute(
        """
        UPDATE AGENCIES
        SET APPROVED =
            CASE 
                WHEN approval_status = 'approved' then TRUE
                ELSE FALSE
            END
    """
    )
    op.execute("""DROP VIEW IF EXISTS agencies_expanded""")
    op.drop_column("agencies", "approval_status")
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
        a.approved,
        a.rejection_reason,
        a.last_approval_editor,
        a.submitter_contact,
        a.agency_created,
        l.locality_name
       FROM agencies a
         LEFT JOIN locations_expanded l ON a.location_id = l.id;
        """
    )
