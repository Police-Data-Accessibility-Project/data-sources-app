"""Clean up data sources table structure

Revision ID: a1a8d636f4dd
Revises: a41df84338bb
Create Date: 2025-10-21 11:33:46.002274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1a8d636f4dd'
down_revision: Union[str, None] = 'a41df84338bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DATA_SOURCES_TABLE_NAME: str = "data_sources"

def upgrade() -> None:
    op.execute("""
    drop view data_sources_expanded
    """)

    op.alter_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="record_type_id",
        nullable=True
    )
    # Drop columns
    op.drop_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="airtable_uid",
    )
    op.drop_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="tags",
    )
    op.drop_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="broken_source_url_as_of"
    )
    op.drop_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="record_download_option_provided"
    )
    op.drop_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="data_source_request"
    )
    op.drop_column(
        table_name=DATA_SOURCES_TABLE_NAME,
        column_name="submission_notes"
    )


    op.execute("""
    create view data_sources_expanded
            (name, description, source_url, agency_supplied, supplying_entity, agency_originated, agency_aggregation,
             coverage_start, coverage_end, updated_at, detail_level, data_portal_type, update_method, readme_url,
             originating_entity, retention_schedule, id, scraper_url, created_at, 
             agency_described_not_in_database, data_portal_type_other,
             access_notes, url_status, record_type_id, record_type_name, access_types, record_formats)
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
        ds.agency_described_not_in_database,
        ds.data_portal_type_other,
        ds.access_notes,
        ds.url_status,
        ds.record_type_id,
        rt.name AS record_type_name,
        ds.access_types,
        ds.record_formats
    FROM
        data_sources ds
        LEFT JOIN record_types rt
                  ON ds.record_type_id = rt.id
    
    """)


def downgrade() -> None:
    pass
