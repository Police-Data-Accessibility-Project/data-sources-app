"""Remove non breaking spaces

Revision ID: 86697daa220c
Revises: a2e1c321a4a1
Create Date: 2025-08-09 19:07:34.462328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86697daa220c'
down_revision: Union[str, None] = 'a2e1c321a4a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    _delete_duplicate_data_sources()
    _remove_non_breaking_spaces()
    _add_constraint_forbidding_nbsp()

def downgrade() -> None:
    _drop_constraint_forbidding_nbsp()

def _remove_non_breaking_spaces() -> None:
    op.execute("""
    update data_sources
    set source_url = replace(source_url, ' ', '')
    where source_url like '% %'
    """)

def _delete_duplicate_data_sources() -> None:
    op.execute("""
    delete from data_sources
    where id in (
        648
    )
    """)

def _add_constraint_forbidding_nbsp() -> None:
    op.execute("""
    ALTER TABLE data_sources
    ADD CONSTRAINT data_sources_source_url_nbsp_check CHECK (source_url NOT LIKE '% %');
    """)

def _drop_constraint_forbidding_nbsp() -> None:
    op.execute("""
    ALTER TABLE data_sources
    DROP CONSTRAINT data_sources_source_url_nbsp_check;
    """)