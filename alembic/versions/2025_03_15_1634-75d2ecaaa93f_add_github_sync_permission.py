"""Add GitHub Sync Permission

Revision ID: 75d2ecaaa93f
Revises: 9687740397b7
Create Date: 2025-03-15 16:34:16.139113

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "75d2ecaaa93f"
down_revision: Union[str, None] = "9687740397b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add GitHub Sync Permission
    op.execute(
        """
        INSERT INTO permissions (permission_name, description)
        VALUES ('github_sync', 'Sync Data Requests with GitHub Issues');
        """
    )


def downgrade() -> None:
    # Remove GitHub Sync Permission
    op.execute(
        """
        DELETE FROM permissions WHERE permission_name = 'github_sync';
        """
    )
