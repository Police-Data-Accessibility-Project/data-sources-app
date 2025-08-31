"""Add constraints to Meta URLs

Revision ID: 2f8bd4749166
Revises: bee37113acc4
Create Date: 2025-08-30 20:11:57.748881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f8bd4749166'
down_revision: Union[str, None] = 'bee37113acc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _remove_url_fragments()
    _add_constraint_forbidding_fragments()


def downgrade() -> None:
    _drop_constraint_forbidding_fragments()

def _remove_url_fragments():
    op.execute("""
    UPDATE agency_meta_urls
    SET url = split_part(url, '#', 1)
    WHERE position('#' in url) > 0;
    """)

def _add_constraint_forbidding_fragments():
    op.execute("""
    ALTER TABLE agency_meta_urls
    ADD CONSTRAINT agency_meta_url_fragment_check CHECK (position('#' in url) = 0);
    """)

def _drop_constraint_forbidding_fragments():
    op.execute("""
    ALTER TABLE agency_meta_urls
    DROP CONSTRAINT agency_meta_url_fragment_check;
    """)