"""Add Agency Meta URLs

Revision ID: bee37113acc4
Revises: d2fda1435aac
Create Date: 2025-08-19 12:18:16.283448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import id_column, created_at_column, updated_at_column, agency_id_column

# revision identifiers, used by Alembic.
revision: str = 'bee37113acc4'
down_revision: Union[str, None] = 'd2fda1435aac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AGENCY_META_URLS_TABLE_NAME = "agency_meta_urls"
AGENCY_TABLE_NAME = "agencies"

def upgrade() -> None:
    _create_agency_meta_urls_table()
    _migrate_homepage_urls_to_agency_meta_urls()
    _delete_homepage_urls_column()

def downgrade() -> None:
    _add_homepage_urls_column()
    _migrate_agency_meta_urls_to_homepage_urls()
    _drop_agency_meta_urls_table()

def _delete_homepage_urls_column():
    op.drop_column(AGENCY_TABLE_NAME, "homepage_url")

def _add_homepage_urls_column():
    op.add_column(
        AGENCY_TABLE_NAME,
        sa.Column("homepage_url", sa.String(), nullable=True),
    )

def _migrate_homepage_urls_to_agency_meta_urls():
    op.execute(
        f"""
        INSERT INTO {AGENCY_META_URLS_TABLE_NAME} (url, agency_id)
        SELECT homepage_url, id
        FROM {AGENCY_TABLE_NAME}
        WHERE homepage_url IS NOT NULL;
        """
    )

def _migrate_agency_meta_urls_to_homepage_urls():
    op.execute(
        f"""
        UPDATE {AGENCY_TABLE_NAME}
        SET homepage_url = (
            SELECT url
            FROM {AGENCY_META_URLS_TABLE_NAME}
            WHERE {AGENCY_META_URLS_TABLE_NAME}.agency_id = {AGENCY_TABLE_NAME}.id
            LIMIT 1
        );
        """
    )

def _create_agency_meta_urls_table():
    op.create_table(
        AGENCY_META_URLS_TABLE_NAME,
        id_column(),
        created_at_column(),
        updated_at_column(),
        sa.Column("url", sa.String(), nullable=False),
        agency_id_column(),
        sa.UniqueConstraint("url", "agency_id", name="agency_meta_urls_url_agency_id_key"),
    )

def _drop_agency_meta_urls_table():
    op.drop_table(AGENCY_META_URLS_TABLE_NAME)