"""Remove agency zip code column

Revision ID: dd2295f7225e
Revises: 8cbea64afdb2
Create Date: 2025-02-13 13:29:50.184101

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dd2295f7225e"
down_revision: Union[str, None] = "8cbea64afdb2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.agencies_expanded;")
    op.drop_column(table_name="agencies", column_name="zip_code")
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

    op.execute(
        """DELETE FROM relation_column
         WHERE (relation = 'agencies' or relation = 'agencies_expanded') AND 
         associated_column = 'zip_code';
         """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.agencies_expanded;")
    op.add_column(
        table_name="agencies",
        column=sa.Column("zip_code", sa.VARCHAR(), autoincrement=False, nullable=True),
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
        a.zip_code,
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

    op.execute(
        """
        With inserted_rows as (
            INSERT INTO relation_column (relation, associated_column)
             VALUES 
                ('agencies', 'zip_code'), 
                ('agencies_expanded', 'zip_code')
            RETURNING id
        )
        INSERT INTO COLUMN_PERMISSION(rc_id, relation_role, access_permission)
        SELECT id, 'STANDARD'::relation_role, 'READ'::access_permission FROM inserted_rows
        UNION ALL
        SELECT id, 'ADMIN'::relation_role, 'READ'::access_permission FROM inserted_rows;
        """
    )
