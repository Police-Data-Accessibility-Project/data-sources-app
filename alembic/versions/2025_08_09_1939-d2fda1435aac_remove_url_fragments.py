"""Remove URL fragments

Revision ID: d2fda1435aac
Revises: 86697daa220c
Create Date: 2025-08-09 19:39:46.734733

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d2fda1435aac"
down_revision: Union[str, None] = "86697daa220c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _delete_duplicate_urls()
    _remove_url_fragments()
    _add_constraint_forbidding_fragments()


def downgrade() -> None:
    _drop_constraint_forbidding_fragments()


def _delete_duplicate_urls():
    op.execute(
        """
        DELETE FROM data_sources WHERE id in (1642, 1074, 1140, 2925, 1547, 1059)
        """
    )


def _remove_url_fragments():
    op.execute("""
    UPDATE data_sources
    SET source_url = split_part(source_url, '#', 1)
    WHERE position('#' in source_url) > 0;
    """)


def _add_constraint_forbidding_fragments() -> None:
    op.execute("""
    ALTER TABLE data_sources
    ADD CONSTRAINT data_sources_source_url_fragment_check CHECK (position('#' in source_url) = 0);
    """)


def _drop_constraint_forbidding_fragments() -> None:
    op.execute("""
    ALTER TABLE data_sources
    DROP CONSTRAINT data_sources_source_url_fragment_check;
    """)
