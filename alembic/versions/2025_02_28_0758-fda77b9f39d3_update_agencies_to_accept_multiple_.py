"""Update agencies to accept multiple locations

Revision ID: fda77b9f39d3
Revises: 070705ddf3a3
Create Date: 2025-02-28 07:58:59.011486

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fda77b9f39d3"
down_revision: Union[str, None] = "070705ddf3a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create `link_agencies_locations` table
    op.create_table(
        "link_agencies_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agency_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["agency_id"],
            ["agencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agency_id", "location_id", name="unique_agency_location"),
    )
    # Create trigger adding to change log
    op.execute(
        """
        CREATE OR REPLACE TRIGGER log_link_agencies_locations_changes
        BEFORE DELETE OR UPDATE 
        ON public.link_agencies_locations
        FOR EACH ROW
        EXECUTE FUNCTION public.log_table_changes();
    """
    )
    # Add agencies location ids to link table
    op.execute(
        """
        INSERT INTO link_agencies_locations (agency_id, location_id)
        SELECT id, location_id
        FROM agencies
        WHERE location_id IS NOT NULL
    """
    )
    # Drop agencies location ids from agencies table
    op.execute("drop view if exists agencies_expanded")
    op.execute("drop view if exists user_pending_notifications")
    op.execute("drop view if exists qualifying_notifications")
    op.execute("drop materialized view if exists typeahead_agencies")
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
            LEFT JOIN link_agencies_locations lal on lal.agency_id = a.id
            LEFT JOIN locations_expanded l ON lal.location_id = l.id
    WITH DATA;
    """
    )
    op.drop_column("agencies", "location_id")

    op.execute(
        """
    CREATE OR REPLACE VIEW public.qualifying_notifications
 AS
 WITH cutoff_point AS (
         SELECT date_trunc('month'::text, CURRENT_DATE::timestamp with time zone) - '1 mon'::interval AS date_range_min,
            date_trunc('month'::text, CURRENT_DATE::timestamp with time zone) AS date_range_max
        )
 SELECT
        CASE
            WHEN dr.request_status = 'Ready to start'::request_status THEN 'Request Ready to Start'::event_type
            WHEN dr.request_status = 'Complete'::request_status THEN 'Request Complete'::event_type
            ELSE NULL::event_type
        END AS event_type,
    dr.id AS entity_id,
    'Data Request'::entity_type AS entity_type,
    dr.title AS entity_name,
    lnk_dr.location_id,
    dr.date_status_last_changed AS event_timestamp
   FROM cutoff_point cp,
    data_requests dr
     JOIN link_locations_data_requests lnk_dr ON lnk_dr.data_request_id = dr.id
  WHERE dr.date_status_last_changed > cp.date_range_min AND dr.date_status_last_changed < cp.date_range_max AND (dr.request_status = 'Ready to start'::request_status OR dr.request_status = 'Complete'::request_status)
UNION ALL
 SELECT 'Data Source Approved'::event_type AS event_type,
    ds.id AS entity_id,
    'Data Source'::entity_type AS entity_type,
    ds.name AS entity_name,
    lal.location_id,
    ds.approval_status_updated_at AS event_timestamp
   FROM cutoff_point cp,
    data_sources ds
     JOIN link_agencies_data_sources lnk ON lnk.data_source_id = ds.id
     JOIN agencies a ON lnk.agency_id = a.id
     LEFT JOIN LINK_AGENCIES_LOCATIONS lal ON lal.agency_id = a.id
  WHERE ds.approval_status_updated_at > cp.date_range_min AND ds.approval_status_updated_at < cp.date_range_max AND ds.approval_status = 'approved'::approval_status;
    """
    )
    op.execute(
        """
    CREATE OR REPLACE VIEW public.user_pending_notifications
     AS
     SELECT DISTINCT q.event_type,
        q.entity_id,
        q.entity_type,
        q.entity_name,
        q.location_id,
        q.event_timestamp,
        l.user_id,
        u.email
       FROM qualifying_notifications q
         JOIN dependent_locations d ON d.dependent_location_id = q.location_id
         JOIN link_user_followed_location l ON l.location_id = q.location_id OR l.location_id = d.parent_location_id
         JOIN users u ON u.id = l.user_id;
    """
    )


def downgrade() -> None:
    # Add agencies location ids to agencies table
    op.add_column("agencies", sa.Column("location_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE agencies
        SET location_id = lal.location_id
        FROM link_agencies_locations lal
        WHERE lal.agency_id = agencies.id
    """
    )
    op.create_unique_constraint(
        "agencies_unique",
        "agencies",
        ["id", "location_id"],
    )
    # Drop trigger adding to change log
    op.execute(
        "DROP TRIGGER IF EXISTS log_link_agencies_locations_changes ON public.link_agencies_locations"
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
    op.execute(
        """
    CREATE OR REPLACE VIEW public.qualifying_notifications
 AS
 WITH cutoff_point AS (
         SELECT date_trunc('month'::text, CURRENT_DATE::timestamp with time zone) - '1 mon'::interval AS date_range_min,
            date_trunc('month'::text, CURRENT_DATE::timestamp with time zone) AS date_range_max
        )
 SELECT
        CASE
            WHEN dr.request_status = 'Ready to start'::request_status THEN 'Request Ready to Start'::event_type
            WHEN dr.request_status = 'Complete'::request_status THEN 'Request Complete'::event_type
            ELSE NULL::event_type
        END AS event_type,
    dr.id AS entity_id,
    'Data Request'::entity_type AS entity_type,
    dr.title AS entity_name,
    lnk_dr.location_id,
    dr.date_status_last_changed AS event_timestamp
   FROM cutoff_point cp,
    data_requests dr
     JOIN link_locations_data_requests lnk_dr ON lnk_dr.data_request_id = dr.id
  WHERE dr.date_status_last_changed > cp.date_range_min AND dr.date_status_last_changed < cp.date_range_max AND (dr.request_status = 'Ready to start'::request_status OR dr.request_status = 'Complete'::request_status)
UNION ALL
 SELECT 'Data Source Approved'::event_type AS event_type,
    ds.id AS entity_id,
    'Data Source'::entity_type AS entity_type,
    ds.name AS entity_name,
    a.location_id,
    ds.approval_status_updated_at AS event_timestamp
   FROM cutoff_point cp,
    data_sources ds
     JOIN link_agencies_data_sources lnk ON lnk.data_source_id = ds.id
     JOIN agencies a ON lnk.agency_id = a.id
  WHERE ds.approval_status_updated_at > cp.date_range_min AND ds.approval_status_updated_at < cp.date_range_max AND ds.approval_status = 'approved'::approval_status;
    """
    )
    op.execute(
        """
    CREATE OR REPLACE VIEW public.user_pending_notifications
     AS
     SELECT DISTINCT q.event_type,
        q.entity_id,
        q.entity_type,
        q.entity_name,
        q.location_id,
        q.event_timestamp,
        l.user_id,
        u.email
       FROM qualifying_notifications q
         JOIN dependent_locations d ON d.dependent_location_id = q.location_id
         JOIN link_user_followed_location l ON l.location_id = q.location_id OR l.location_id = d.parent_location_id
         JOIN users u ON u.id = l.user_id;
    """
    )
    op.execute("""drop materialized view if exists typeahead_agencies""")
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
         LEFT JOIN locations_expanded l ON a.location_id = l.id
    WITH DATA;
    """
    )

    # Drop `link_agencies_locations` table
    op.drop_table("link_agencies_locations")
