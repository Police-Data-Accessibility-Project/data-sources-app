"""Add data source post permission

Revision ID: d7634d1796d7
Revises: f001f28e8ab2
Create Date: 2025-04-05 16:20:20.397369

"""

from typing import Sequence, Union


from middleware.alembic_helpers import add_permission, remove_permission

# revision identifiers, used by Alembic.
revision: str = "d7634d1796d7"
down_revision: Union[str, None] = "f001f28e8ab2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    add_permission(
        permission_name="source_collector_data_sources",
        description="Enables creation of data sources via `source-collector/data-sources` `POST` endpoint",
    )


def downgrade() -> None:
    remove_permission(permission_name="source_collector_data_sources")
