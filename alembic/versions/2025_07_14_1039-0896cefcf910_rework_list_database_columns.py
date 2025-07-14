"""Rework list database columns

Revision ID: 0896cefcf910
Revises: 4f9431c309e3
Create Date: 2025-07-14 10:39:59.888189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0896cefcf910'
down_revision: Union[str, None] = '4f9431c309e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DATA_SOURCES_TABLE_NAME = "data_sources"
DATA_REQUESTS_TABLE_NAME = "data_requests"

table_column_type = [
    (DATA_REQUESTS_TABLE_NAME, 'record_types_required', 'record_type[]'),
    (DATA_SOURCES_TABLE_NAME, 'access_types', 'access_type[]'),
    (DATA_SOURCES_TABLE_NAME, 'tags', 'text[]'),
    (DATA_SOURCES_TABLE_NAME, 'record_formats', 'text[]'),
]


def upgrade() -> None:
    for table_name, column_name, pg_array_type in table_column_type:
        enforce_not_null_array_column(table_name, column_name, pg_array_type)


def downgrade() -> None:
    for table_name, column_name, _ in table_column_type:
        relax_not_null_array_column(table_name, column_name)



def relax_not_null_array_column(
    table_name: str,
    column_name: str,
):
    op.alter_column(
        table_name,
        column_name,
        nullable=True,
        server_default=None
    )


def enforce_not_null_array_column(
    table_name: str,
    column_name: str,
    pg_array_type: str
):
    """
    Updates a PostgreSQL array column in-place to:
    1. Replace NULLs with empty list
    2. Set default to empty list
    3. Apply NOT NULL constraint

    Args:
        table_name: The name of the table (e.g., 'search_links')
        column_name: The name of the column (e.g., 'linked_table_name')
        pg_array_type: PostgreSQL type for array (e.g., 'varchar[]', 'integer[]')
    """

    # 1. Replace NULLs with empty list
    op.execute(
        f"""
        UPDATE {table_name}
        SET {column_name} = '{{}}'
        WHERE {column_name} IS NULL
        """
    )

    # 2. Set default to empty list
    op.alter_column(
        table_name,
        column_name,
        server_default=sa.text(f"'{{}}'::{pg_array_type}")
    )

    # 3. Apply NOT NULL constraint
    op.alter_column(
        table_name,
        column_name,
        nullable=False
    )