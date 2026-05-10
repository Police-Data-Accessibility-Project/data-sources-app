"""drop data_sources_expanded view

Revision ID: a3fcd7a36a70
Revises: 71374f18982c
Create Date: 2026-05-02 08:39:23.972345

The data_sources_expanded view exposed the data_sources table joined with
record_types to surface record_type_name. We replace it with a SQLAlchemy
column_property on the DataSource model that issues an equivalent correlated
subquery, eliminating the need for the view (and the migration friction it
caused).
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a3fcd7a36a70"
down_revision: Union[str, None] = "71374f18982c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS public.data_sources_expanded")


def downgrade() -> None:
    op.execute(
        """
        CREATE VIEW public.data_sources_expanded
            (name, description, source_url, agency_supplied, supplying_entity,
             agency_originated, agency_aggregation, coverage_start, coverage_end,
             updated_at, detail_level, data_portal_type, update_method, readme_url,
             originating_entity, retention_schedule, id, scraper_url, created_at,
             agency_described_not_in_database, data_portal_type_other,
             access_notes, url_status, record_type_id, record_type_name,
             access_types, record_formats)
        AS
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
            public.data_sources ds
            LEFT JOIN public.record_types rt
                      ON ds.record_type_id = rt.id
        """
    )
