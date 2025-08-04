"""Remove unused data_sources logic

Revision ID: b4c716990c48
Revises: 0896cefcf910
Create Date: 2025-08-04 11:50:05.889810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = 'b4c716990c48'
down_revision: Union[str, None] = '0896cefcf910'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "data_sources"
SOURCE_URL_COLUMN_NAME = "source_url"
URL_STATUS_COLUMN_NAME = "url_status"
URL_STATUS_ENUM_NAME = "url_status"


def upgrade() -> None:
    _remove_unused_url_status_enums()
    _make_source_url_not_nullable()

def downgrade() -> None:
    _make_source_url_nullable()
    _add_url_status_enums()

def _remove_unused_url_status_enums():
    switch_enum_type(
        table_name=TABLE_NAME,
        column_name=URL_STATUS_COLUMN_NAME,
        enum_name=URL_STATUS_ENUM_NAME,
        new_enum_values=[
            'ok',
            'broken',
        ]
    )


def _add_url_status_enums():
    switch_enum_type(
        table_name=TABLE_NAME,
        column_name=URL_STATUS_COLUMN_NAME,
        enum_name=URL_STATUS_ENUM_NAME,
        new_enum_values=[
            'ok',
            'broken',
            'available',
            'none found',
        ]
    )

def _make_source_url_nullable():
    op.alter_column(TABLE_NAME, SOURCE_URL_COLUMN_NAME, nullable=True)

def _make_source_url_not_nullable():
    op.alter_column(TABLE_NAME, SOURCE_URL_COLUMN_NAME, nullable=False)
