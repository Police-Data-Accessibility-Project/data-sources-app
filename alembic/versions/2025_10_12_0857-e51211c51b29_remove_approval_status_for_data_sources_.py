"""Remove approval status for data sources and agencies

Revision ID: e51211c51b29
Revises: 8c3153d94dfb
Create Date: 2025-10-12 08:57:00.734088

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e51211c51b29"
down_revision: Union[str, None] = "8c3153d94dfb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _delete_agencies_and_data_sources_without_approval():
    op.execute("""DELETE FROM data_sources WHERE approval_status != 'approved'""")
    op.execute("""DELETE FROM agencies WHERE approval_status != 'approved'""")


def upgrade() -> None:
    _delete_agencies_and_data_sources_without_approval()
    _drop_views()
    _drop_columns()
    _rebuild_views()
    op.execute("drop trigger update_approval_status_updated_at on data_sources;")
    op.execute("drop function update_approval_status_updated_at;")


def _rebuild_views():
    op.execute("""
    create materialized view distinct_source_urls as
    SELECT DISTINCT rtrim(ltrim(ltrim(ltrim(data_sources.source_url::text, 'https://'::text), 'http://'::text),
                                'www.'::text), '/'::text) AS base_url,
                    data_sources.source_url               AS original_url
    FROM data_sources
    WHERE data_sources.source_url IS NOT NULL;
    """)
    op.execute("""
    create materialized view typeahead_agencies as
    SELECT
        a.id,
        a.name,
        a.jurisdiction_type,
        l.state_iso,
        l.locality_name AS municipality,
        l.county_name
    FROM
        agencies a
            LEFT JOIN link_agencies_locations lal ON lal.agency_id = a.id
            LEFT JOIN locations_expanded l ON lal.location_id = l.id
    """)
    op.execute("""
    create view data_sources_expanded
            (name, description, source_url, agency_supplied, supplying_entity, agency_originated, agency_aggregation,
             coverage_start, coverage_end, updated_at, detail_level, data_portal_type, update_method, readme_url,
             originating_entity, retention_schedule, id, scraper_url, created_at, submission_notes, 
             agency_described_not_in_database, data_portal_type_other,
             data_source_request, broken_source_url_as_of, access_notes, url_status, record_type_id,
             record_type_name, access_types, tags, record_formats)
    as
    SELECT
        ds.name,
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
        ds.agency_described_not_in_database,
        ds.data_portal_type_other,
        ds.data_source_request,
        ds.broken_source_url_as_of,
        ds.access_notes,
        ds.url_status,
        ds.record_type_id,
        rt.name AS record_type_name,
        ds.access_types,
        ds.tags,
        ds.record_formats
    FROM
        data_sources ds
        LEFT JOIN record_types rt
                  ON ds.record_type_id = rt.id
        
    """)


def _drop_views():
    op.execute("""drop view data_sources_expanded""")
    op.execute("""drop materialized view distinct_source_urls""")
    op.execute("""drop materialized view typeahead_agencies""")


def _drop_columns():
    op.drop_column(table_name="data_sources", column_name="approval_status")
    op.drop_column(table_name="data_sources", column_name="last_approval_editor")
    op.drop_column(table_name="data_sources", column_name="submitter_contact_info")
    op.drop_column(table_name="data_sources", column_name="approval_status_updated_at")
    op.drop_column(table_name="agencies", column_name="approval_status")
    op.drop_column(table_name="agencies", column_name="last_approval_editor")
    op.drop_column(table_name="agencies", column_name="creator_user_id")
    op.drop_column(table_name="agencies", column_name="rejection_reason")
    op.drop_column(table_name="agencies", column_name="submitter_contact")


def downgrade() -> None:
    pass
