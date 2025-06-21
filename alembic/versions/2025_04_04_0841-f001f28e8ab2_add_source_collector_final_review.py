"""Add source_collector_final_review permission

Revision ID: f001f28e8ab2
Revises: c1d862a9a587
Create Date: 2025-04-04 08:41:39.820627

"""

from typing import Sequence, Union


from middleware.alembic_helpers import add_permission, remove_permission

# revision identifiers, used by Alembic.
revision: str = "f001f28e8ab2"
down_revision: Union[str, None] = "c1d862a9a587"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    add_permission(
        permission_name="source_collector_final_review",
        description="Allows access to /review namespace in source collector app",
    )


def downgrade() -> None:
    remove_permission(permission_name="source_collector_final_review")
