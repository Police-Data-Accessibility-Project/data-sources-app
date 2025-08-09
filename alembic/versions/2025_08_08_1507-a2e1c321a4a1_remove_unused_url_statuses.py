"""Remove unused url statuses

Revision ID: a2e1c321a4a1
Revises: 0da785aaf39a
Create Date: 2025-08-08 15:07:19.653336

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a2e1c321a4a1"
down_revision: Union[str, None] = "0da785aaf39a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "data_sources"
ENUM_NAME = "url_status"
COLUMN_NAME = "url_status"


def upgrade() -> None:
    _drop_view()

    op.execute(
        "CREATE TYPE url_status_enum AS ENUM ('ok', 'broken');",
    )
    # Remove default value
    op.execute(f"ALTER TABLE {TABLE_NAME} ALTER COLUMN {COLUMN_NAME} SET DEFAULT NULL;")

    op.execute("""
        ALTER TABLE data_sources
        ALTER COLUMN url_status TYPE url_status_enum
        USING url_status::text::url_status_enum;
    """)

    op.execute(
        """ALTER TABLE data_sources
        ALTER COLUMN url_status SET DEFAULT 'ok';
        """
    )

    op.execute(
        "DROP TYPE url_status;",
    )

    _create_view()


def downgrade() -> None:
    _drop_view()

    op.execute(
        "CREATE TYPE url_status AS ENUM ('ok', 'broken', 'available', 'none found');",
    )

    op.execute(f"ALTER TABLE {TABLE_NAME} ALTER COLUMN {COLUMN_NAME} SET DEFAULT NULL;")

    op.execute("""
        ALTER TABLE data_sources
        ALTER COLUMN url_status TYPE url_status
        USING url_status::text::url_status;
    """)

    op.execute("""
        ALTER TABLE data_sources
        ALTER COLUMN url_status SET DEFAULT 'ok';
    """)

    op.execute(
        "DROP TYPE url_status_enum;",
    )

    _create_view()


def _drop_view():
    op.execute("DROP VIEW data_sources_expanded;")


def _create_view():
    op.execute(
        """
        create view data_sources_expanded
            (name, description, source_url, agency_supplied, supplying_entity, agency_originated, agency_aggregation,
             coverage_start, coverage_end, updated_at, detail_level, data_portal_type, update_method, readme_url,
             originating_entity, retention_schedule, id, scraper_url, created_at, submission_notes, rejection_note,
             last_approval_editor, submitter_contact_info, agency_described_not_in_database, data_portal_type_other,
             data_source_request, broken_source_url_as_of, access_notes, url_status, approval_status, record_type_id,
             record_type_name, access_types, tags, record_formats, approval_status_updated_at)
as
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
         LEFT JOIN record_types rt ON ds.record_type_id = rt.id
        """
    )
