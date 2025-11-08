"""Normalize Meta URLs

Revision ID: 88708d999de4
Revises: cea759e04756
Create Date: 2025-11-08 15:19:26.858171

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import agency_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = "88708d999de4"
down_revision: Union[str, None] = "cea759e04756"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _update_meta_url_unique_constraint():
    # Add new constraint
    op.create_unique_constraint(
        "uq_meta_urls_url",
        "meta_urls",
        ["url"],
    )


def upgrade() -> None:
    _delete_existing_meta_urls()
    _rename_agency_meta_urls_to_meta_urls()
    _add_meta_url_agency_link_table()
    _remove_agency_id_column_from_meta_urls_table()
    _update_meta_url_unique_constraint()


def _delete_existing_meta_urls():
    op.execute("""
    DELETE FROM AGENCY_META_URLS
    """)


def _add_meta_url_agency_link_table():
    op.create_table(
        "link_agencies__meta_urls",
        agency_id_column(),
        sa.Column(
            "meta_url_id",
            sa.Integer(),
            nullable=False,
        ),
        created_at_column(),
        sa.ForeignKeyConstraint(
            ["meta_url_id"],
            ["meta_urls.id"],
            name="agency_meta_url_link_meta_url_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("agency_id", "meta_url_id"),
    )


def _remove_agency_id_column_from_meta_urls_table():
    op.drop_column("meta_urls", "agency_id")


def _rename_agency_meta_urls_to_meta_urls():
    op.rename_table("agency_meta_urls", "meta_urls")


def downgrade() -> None:
    pass
