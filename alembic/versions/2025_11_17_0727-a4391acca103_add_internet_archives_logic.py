"""Add internet archives logic

Revision ID: a4391acca103
Revises: 88708d999de4
Create Date: 2025-11-17 07:27:17.157420

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = "a4391acca103"
down_revision: Union[str, None] = "88708d999de4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    remove_broken_url_as_of_trigger()
    add_internet_archive_url_to_data_sources()
    add_internet_archive_url_to_meta_urls()
    add_url_status_to_meta_urls()


def remove_broken_url_as_of_trigger():
    # Remove trigger as well
    op.execute("DROP TRIGGER IF EXISTS update_broken_source_url_as_of ON data_sources")


def add_internet_archive_url_to_data_sources():
    op.add_column(
        "data_sources",
        sa.Column(
            "internet_archive_url",
            sa.Text(),
            nullable=True,
        ),
    )


def add_internet_archive_url_to_meta_urls():
    op.add_column(
        "meta_urls",
        sa.Column(
            "internet_archive_url",
            sa.Text(),
            nullable=True,
        ),
    )


def add_url_status_to_meta_urls():
    url_status_enum = ENUM(
        "broken",
        "ok",
        name="url_status_enum",
        create_type=False,
    )

    op.add_column(
        "meta_urls",
        sa.Column(
            "url_status",
            url_status_enum,
            nullable=False,
            server_default="ok",
        ),
    )


def downgrade() -> None:
    pass
