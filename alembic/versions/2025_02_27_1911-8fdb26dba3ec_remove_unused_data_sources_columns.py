"""Remove unused data_sources columns

Revision ID: 8fdb26dba3ec
Revises: 59a0070a8a83
Create Date: 2025-02-27 19:11:36.823591

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8fdb26dba3ec"
down_revision: Union[str, None] = "59a0070a8a83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("DROP VIEW IF EXISTS data_sources_expanded")

    op.drop_column("data_sources", "submitted_name")
    op.drop_column("data_sources", "agency_described_submitted")

    op.execute("DROP TRIGGER set_source_name on data_sources")
    op.execute("DROP FUNCTION set_source_name()")

    op.execute(
        """
    CREATE OR REPLACE VIEW public.data_sources_expanded
 AS
 SELECT ds.name,
    ds.description,
    ds.source_url,
    ds.agency_supplied,
    ds.supplying_entity,
    ds.agency_originated,
    ds.agency_aggregation,
    ds.coverage_start,
    ds.coverage_end,
    ds.updated_at,
    ds.detail_level,
    ds.data_portal_type,
    ds.update_method,
    ds.readme_url,
    ds.originating_entity,
    ds.retention_schedule,
    ds.id,
    ds.scraper_url,
    ds.created_at,
    ds.submission_notes,
    ds.rejection_note,
    ds.last_approval_editor,
    ds.submitter_contact_info,
    ds.agency_described_not_in_database,
    ds.data_portal_type_other,
    ds.data_source_request,
    ds.broken_source_url_as_of,
    ds.access_notes,
    ds.url_status,
    ds.approval_status,
    ds.record_type_id,
    rt.name AS record_type_name,
    ds.access_types,
    ds.tags,
    ds.record_formats,
    ds.approval_status_updated_at
   FROM data_sources ds
     LEFT JOIN record_types rt ON ds.record_type_id = rt.id;
    
    """
    )


def downgrade():
    op.add_column(
        "data_sources", sa.Column("submitted_name", sa.VARCHAR(), nullable=True)
    )
    op.add_column(
        "data_sources",
        sa.Column("agency_described_submitted", sa.VARCHAR(), nullable=True),
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION public.set_source_name()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
    AS $BODY$
    BEGIN
        IF NEW.name IS NULL THEN
            NEW.name := NEW.submitted_name;
        END IF;
        RETURN NEW;
    END
    $BODY$;
    """
    )

    op.execute(
        """
    CREATE OR REPLACE TRIGGER set_source_name
    BEFORE INSERT
    ON public.data_sources
    FOR EACH ROW
    EXECUTE FUNCTION public.set_source_name();
    """
    )

    op.execute("DROP VIEW IF EXISTS data_sources_expanded")
    op.execute(
        """
    CREATE OR REPLACE VIEW public.data_sources_expanded
 AS
 SELECT ds.name,
    ds.submitted_name,
    ds.description,
    ds.source_url,
    ds.agency_supplied,
    ds.supplying_entity,
    ds.agency_originated,
    ds.agency_aggregation,
    ds.coverage_start,
    ds.coverage_end,
    ds.updated_at,
    ds.detail_level,
    ds.data_portal_type,
    ds.update_method,
    ds.readme_url,
    ds.originating_entity,
    ds.retention_schedule,
    ds.id,
    ds.scraper_url,
    ds.created_at,
    ds.submission_notes,
    ds.rejection_note,
    ds.last_approval_editor,
    ds.submitter_contact_info,
    ds.agency_described_submitted,
    ds.agency_described_not_in_database,
    ds.data_portal_type_other,
    ds.data_source_request,
    ds.broken_source_url_as_of,
    ds.access_notes,
    ds.url_status,
    ds.approval_status,
    ds.record_type_id,
    rt.name AS record_type_name,
    ds.access_types,
    ds.tags,
    ds.record_formats,
    ds.approval_status_updated_at
   FROM data_sources ds
     LEFT JOIN record_types rt ON ds.record_type_id = rt.id;
    """
    )
