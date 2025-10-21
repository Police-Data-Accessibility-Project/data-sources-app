"""Remove unneeded agencies columns

Revision ID: a41df84338bb
Revises: e51211c51b29
Create Date: 2025-10-21 09:55:20.961243

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a41df84338bb"
down_revision: Union[str, None] = "e51211c51b29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AGENCIES_TABLE_NAME: str = "agencies"


def upgrade() -> None:
    op.alter_column(
        table_name=AGENCIES_TABLE_NAME,
        column_name="agency_created",
        new_column_name="created_at",
    )
    op.drop_column(AGENCIES_TABLE_NAME, "multi_agency")
    op.drop_column(AGENCIES_TABLE_NAME, "airtable_agency_last_modified")
    op.drop_column(AGENCIES_TABLE_NAME, "airtable_uid")
    op.execute("""
    DROP TRIGGER IF EXISTS set_agency_updated_at ON public.agencies
    """)
    op.execute("""
    DROP FUNCTION IF EXISTS update_airtable_agency_last_modified_column
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION update_agency_updated_at_column()
        
    RETURNS TRIGGER language plpgsql AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$
    """)

    op.execute("""
    CREATE TRIGGER set_agency_updated_at
    BEFORE UPDATE ON public.agencies
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION update_agency_updated_at_column()
    """)


def downgrade() -> None:
    pass
