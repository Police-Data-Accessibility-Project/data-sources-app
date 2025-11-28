"""Update permission names

Revision ID: 71374f18982c
Revises: 6e63a9edc949
Create Date: 2025-11-27 13:13:18.948519

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "71374f18982c"
down_revision: Union[str, None] = "6e63a9edc949"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _update_permission_names(old_name: str, new_name: str):
    op.execute(
        f"UPDATE permissions "
        f"SET permission_name = '{new_name}' "
        f"WHERE permission_name = '{old_name}'"
    )


def _remove_archive_write_permission():
    op.execute("DELETE FROM permissions WHERE permission_name = 'archive_write'")


def _update_permission_descriptions(
    name: str,
    description: str,
):
    op.execute(
        f"UPDATE permissions "
        f"SET description = '{description}' "
        f"WHERE permission_name = '{name}'"
    )


def upgrade() -> None:
    _remove_archive_write_permission()
    old_new_mappings: dict[str, str] = {
        "db_write": "write_data",
        "notifications": "send_notifications",
        "source_collector": "access_source_collector",
        "user_create_update": "create_update_user",
        "github_sync": "sync_to_github",
        "source_collector_data_sources": "call_ds_source_collector_endpoints",
    }
    for old_name, new_name in old_new_mappings.items():
        _update_permission_names(old_name=old_name, new_name=new_name)

    name_description_mappings: dict[str, str] = {
        "write_data": "Use endpoints that write data to the database.",
        "send_notifications": "Use endpoints that send notifications.",
        "access_source_collector": "Use endpoints that access the source collector.",
        "create_update_user": "Use endpoints that create or update users.",
        "sync_to_github": "Use endpoints that sync to GitHub.",
        "call_ds_source_collector_endpoints": "Use endpoints that call the data source collector endpoints.",
    }
    for name, description in name_description_mappings.items():
        _update_permission_descriptions(name=name, description=description)


def downgrade() -> None:
    pass
