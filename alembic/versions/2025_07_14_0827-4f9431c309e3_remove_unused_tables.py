"""Remove unused tables

Revision ID: 4f9431c309e3
Revises: d6c5ae86c776
Create Date: 2025-07-14 08:27:00.384278

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import drop_enum, enum_column

# revision identifiers, used by Alembic.
revision: str = "4f9431c309e3"
down_revision: Union[str, None] = "d6c5ae86c776"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEARCH_LINKS_TABLE_NAME = "search_links"
SEARCH_RESULTS_TABLE_NAME = "search_results"
SEARCH_QUEUE_TABLE_NAME = "search_queue"
SEARCH_BATCH_INFO_TABLE_NAME = "search_batch_info"

SEARCH_STATUS_ENUM_NAME = "search_status"
SEARCH_RESULT_ENUM_NAME = "search_result"


def upgrade() -> None:
    op.drop_table(SEARCH_RESULTS_TABLE_NAME)
    op.drop_table(SEARCH_LINKS_TABLE_NAME)
    op.drop_table(SEARCH_QUEUE_TABLE_NAME)
    op.drop_table(SEARCH_BATCH_INFO_TABLE_NAME)

    drop_enum(SEARCH_STATUS_ENUM_NAME)
    drop_enum(SEARCH_RESULT_ENUM_NAME)


def downgrade() -> None:
    op.execute(
        "create type search_result as enum ('found_results', 'no_results_found');"
    )
    _create_search_batch_info_table()
    _create_search_queue_table()
    _create_search_links_table()
    _create_search_results_table()


def _create_search_results_table():
    op.create_table(
        SEARCH_RESULTS_TABLE_NAME,
        sa.Column("result_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "search_id",
            sa.Integer,
            sa.ForeignKey("search_queue.search_id"),
            nullable=False,
        ),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=512)),
        sa.Column("snippet", sa.Text),
    )


def _create_search_queue_table():
    op.create_table(
        SEARCH_QUEUE_TABLE_NAME,
        sa.Column("search_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "batch_id",
            sa.Integer,
            sa.ForeignKey("search_batch_info.batch_id"),
            nullable=False,
        ),
        sa.Column("search_query", sa.Text, nullable=False),
        sa.Column("executed_datetime", sa.TIMESTAMP),
        enum_column(
            "status",
            enum_name=SEARCH_STATUS_ENUM_NAME,
            enum_values=["pending", "completed", "error", "no_results"],
        ),
    )


def _create_search_links_table():
    op.create_table(
        SEARCH_LINKS_TABLE_NAME,
        sa.Column("link_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "search_id",
            sa.Integer,
            sa.ForeignKey("search_queue.search_id"),
            nullable=False,
        ),
        sa.Column("link_description", sa.Text),
        sa.Column("linked_table_name", sa.ARRAY(sa.String), nullable=False),
        sa.Column("linked_column_name", sa.ARRAY(sa.String), nullable=False),
        sa.Column("linked_column_id", sa.Integer, nullable=False),
    )


def _create_search_batch_info_table():
    op.create_table(
        SEARCH_BATCH_INFO_TABLE_NAME,
        sa.Column("batch_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("short_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column(
            "initiated_datetime",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
