"""Remove agency state county and municipality columns

Revision ID: 8cbea64afdb2
Revises: 0d9b984683a5
Create Date: 2025-02-13 12:26:39.056537

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8cbea64afdb2"
down_revision: Union[str, None] = "0d9b984683a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(
        table_name="agencies",
        column_name="state_iso",
    )
    op.drop_column(
        table_name="agencies",
        column_name="county_fips",
    )
    op.drop_column(
        table_name="agencies",
        column_name="county_name",
    )
    op.drop_column(
        table_name="agencies",
        column_name="municipality",
    )
    op.execute(
        """DELETE FROM relation_column
         WHERE relation = 'agencies' AND 
         associated_column IN ('state_iso', 'county_fips', 'county_name', 'municipality');
         """
    )


def downgrade() -> None:
    op.add_column(
        table_name="agencies",
        column=sa.Column(
            "municipality", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        table_name="agencies",
        column=sa.Column(
            "county_name", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        table_name="agencies",
        column=sa.Column(
            "county_fips", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        table_name="agencies",
        column=sa.Column("state_iso", sa.VARCHAR(), autoincrement=False, nullable=True),
    )

    op.execute(
        """
        With inserted_rows as (
            INSERT INTO relation_column (relation, associated_column)
             VALUES 
                ('agencies', 'municipality'), 
                ('agencies', 'county_name'), 
                ('agencies', 'county_fips'), 
                ('agencies', 'state_iso')
             RETURNING id
        )
        INSERT INTO COLUMN_PERMISSION(rc_id, relation_role, access_permission)
        SELECT id, 'STANDARD'::relation_role, 'READ'::access_permission FROM inserted_rows
        UNION ALL
        SELECT id, 'ADMIN'::relation_role, 'READ'::access_permission FROM inserted_rows;
        """
    )
