"""Create archive_write_permission

Revision ID: 4713a996cf91
Revises: da63f84a9f34
Create Date: 2025-02-25 18:26:00.053199

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4713a996cf91"
down_revision: Union[str, None] = "da63f84a9f34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    INSERT INTO permissions 
    (permission_name, description) VALUES 
    ('archive_write', 'Enables archiving of data sources');
    """
    )


def downgrade() -> None:
    op.execute(
        """
    DELETE FROM permissions WHERE permission_name = 'archive_write';
    """
    )
