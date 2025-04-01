"""Add creator_user_id to agencies

Revision ID: c1d862a9a587
Revises: 2f6972890d82
Create Date: 2025-03-31 16:30:15.711834

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1d862a9a587"
down_revision: Union[str, None] = "2f6972890d82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agencies", sa.Column("creator_user_id", sa.Integer(), nullable=True))
    # Create a foreign key constraint
    op.create_foreign_key(
        "agencies_creator_user_id_fkey",
        "agencies",
        "users",
        ["creator_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_column("agencies", "creator_user_id")
