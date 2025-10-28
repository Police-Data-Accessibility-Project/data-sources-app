"""Add meta urls updated at trigger

Revision ID: cea759e04756
Revises: f50dc5f69fc4
Create Date: 2025-10-25 16:13:21.507679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cea759e04756'
down_revision: Union[str, None] = 'f50dc5f69fc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column() 
            RETURNS TRIGGER AS $$ 
        BEGIN 
            NEW.updated_at = CURRENT_TIMESTAMP; 
            RETURN NEW; 
        END; $$ language 'plpgsql';
        """
    )
    op.execute("""
    CREATE TRIGGER meta_urls_updated_at_trigger
    BEFORE UPDATE ON agency_meta_urls
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    pass
