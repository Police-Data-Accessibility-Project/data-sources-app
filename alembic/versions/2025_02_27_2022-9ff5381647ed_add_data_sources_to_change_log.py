"""Add data_sources to change_log

Revision ID: 9ff5381647ed
Revises: 8fdb26dba3ec
Create Date: 2025-02-27 20:22:41.555609

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9ff5381647ed"
down_revision: Union[str, None] = "8fdb26dba3ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE TRIGGER log_data_sources_changes
    BEFORE DELETE OR UPDATE 
    ON public.data_sources
    FOR EACH ROW
    EXECUTE FUNCTION public.log_table_changes();
    """
    )


def downgrade() -> None:
    op.execute(
        """
    DROP TRIGGER log_data_sources_changes on data_sources
    """
    )
