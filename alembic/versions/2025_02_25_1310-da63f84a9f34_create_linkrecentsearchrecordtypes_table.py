"""Create LinkRecentSearchRecordTypes table

Revision ID: da63f84a9f34
Revises: 2f5d03d58839
Create Date: 2025-02-25 13:10:36.133597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da63f84a9f34"
down_revision: Union[str, None] = "2f5d03d58839"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "link_recent_search_record_types",
        sa.Column("id", sa.Integer, primary_key=True),
        # Recent search ID, foreign key to recent_searches
        sa.Column("recent_search_id", sa.Integer, nullable=False),
        # Record type ID, foreign key to record_types
        sa.Column("record_type_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ["recent_search_id"], ["recent_searches.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["record_type_id"], ["record_types.id"], ondelete="CASCADE"
        ),
    )


def downgrade() -> None:
    op.drop_table("link_recent_search_record_types")
