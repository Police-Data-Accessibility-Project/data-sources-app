"""Rename link tables

Revision ID: 6e63a9edc949
Revises: a4391acca103
Create Date: 2025-11-18 19:24:55.576785

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6e63a9edc949"
down_revision: Union[str, None] = "a4391acca103"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    rename_mappings = {
        "link_agencies_data_sources": "link_agencies__data_sources",
        "link_agencies_locations": "link_agencies__locations",
        "link_data_sources_data_requests": "link_data_requests__data_sources",
        "link_locations_data_requests": "link_data_requests__locations",
        "link_recent_search_record_categories": "link_recent_searches__record_categories",
        "link_recent_search_record_types": "link_recent_searches__record_types",
        "user_permissions": "link_users__permissions",
    }
    for old_name, new_name in rename_mappings.items():
        op.rename_table(old_name, new_name)


def downgrade() -> None:
    pass
