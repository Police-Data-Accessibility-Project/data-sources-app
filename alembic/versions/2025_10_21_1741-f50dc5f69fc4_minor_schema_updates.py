"""Minor schema updates

Revision ID: f50dc5f69fc4
Revises: a1a8d636f4dd
Create Date: 2025-10-21 17:41:31.007124

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f50dc5f69fc4"
down_revision: Union[str, None] = "a1a8d636f4dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("data_sources", "source_url", nullable=False)
    op.execute("drop view data_sources_expanded")
    op.execute("drop view record_types_expanded")
    update_record_type_name_column()
    _rebuild_data_sources_expanded_view()
    _rebuild_record_types_view()


def update_record_type_name_column():
    op.execute(
        """
        alter table public.record_types
            add column name_new record_type
        """
    )
    op.execute(
        """
        update public.record_types
        set name_new = name::record_type
        """
    )
    op.execute(
        """
        alter table public.record_types
            rename column name to name_old
        """
    )
    op.execute(
        """
        alter table public.record_types
            rename column name_new to name
        """
    )
    op.execute(
        """
        alter table public.record_types
            drop column name_old
            """
    )


def _rebuild_record_types_view():
    op.execute("""
        create view record_types_expanded (record_type_id, record_type_name, record_category_id, record_category_name) as
    SELECT
        rt.id AS record_type_id,
        rt.name AS record_type_name,
        rc.id AS record_category_id,
        rc.name AS record_category_name
    FROM
        record_types rt
        JOIN record_categories rc
             ON rt.category_id = rc.id;
    """)


def _rebuild_data_sources_expanded_view():
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
