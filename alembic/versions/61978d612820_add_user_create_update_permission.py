"""Add user create update permission

Revision ID: 61978d612820
Revises: 83090d813802
Create Date: 2025-02-12 10:56:16.651682

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "61978d612820"
down_revision: Union[str, None] = "83090d813802"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

foreign_key_name = "user_permissions_permission_id_fkey"


def upgrade() -> None:
    op.drop_constraint(
        constraint_name=foreign_key_name,
        table_name="user_permissions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        constraint_name=foreign_key_name,
        source_table="user_permissions",
        referent_table="permissions",
        local_cols=["permission_id"],
        remote_cols=["permission_id"],
        ondelete="CASCADE",
    )

    op.execute(
        """
        INSERT INTO PERMISSIONS(
            permission_name, description
        ) VALUES (
            'user_create_update', 
            'Allow user creation and update'
        );
        """
    )


def downgrade() -> None:

    op.execute(
        """
        DELETE FROM PERMISSIONS
        WHERE permission_name = 'user_create_update';
        """
    )

    op.drop_constraint(
        constraint_name=foreign_key_name,
        table_name="user_permissions",
        type_="foreignkey",
    )

    op.create_foreign_key(
        constraint_name=foreign_key_name,
        source_table="user_permissions",
        referent_table="permissions",
        local_cols=["permission_id"],
        remote_cols=["permission_id"],
        ondelete="NO ACTION",
    )
