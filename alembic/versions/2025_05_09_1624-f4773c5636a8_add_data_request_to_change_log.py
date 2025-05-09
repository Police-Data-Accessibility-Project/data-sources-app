"""Add data request to change log

Revision ID: f4773c5636a8
Revises: 7b0b4eaa9764
Create Date: 2025-05-09 16:24:27.577869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4773c5636a8'
down_revision: Union[str, None] = '7b0b4eaa9764'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE TRIGGER log_data_request_changes
    BEFORE DELETE OR UPDATE 
    ON public.data_requests
    FOR EACH ROW
    EXECUTE FUNCTION public.log_table_changes();
    """
    )


def downgrade() -> None:
    op.execute(
        """
    DROP TRIGGER log_data_request_changes on data_requests
    """
    )
