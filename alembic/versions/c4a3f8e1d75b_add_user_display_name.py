"""Add user display_name

Revision ID: c4a3f8e1d75b
Revises: 71374f18982c
Create Date: 2026-05-02 08:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c4a3f8e1d75b"
down_revision: Union[str, None] = "71374f18982c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users.display_name -- nullable first so we can backfill existing rows
    op.add_column(
        "users",
        sa.Column("display_name", sa.String(length=30), nullable=True),
    )

    # Backfill existing rows with the user id, left-padded to 3 chars so it
    # satisfies the 3-character minimum length validator. Uniqueness is
    # guaranteed because user.id is unique.
    op.execute("UPDATE users SET display_name = LPAD(id::text, 3, '0')")

    op.alter_column("users", "display_name", nullable=False)

    # Case-insensitive uniqueness via a functional unique index on LOWER().
    op.create_index(
        "uq_users_display_name_lower",
        "users",
        [sa.text("LOWER(display_name)")],
        unique=True,
    )

    # pending_users.display_name -- optional field captured at signup so the
    # display name can be carried over to the user row at email validation.
    op.add_column(
        "pending_users",
        sa.Column("display_name", sa.String(length=30), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("pending_users", "display_name")
    op.drop_index("uq_users_display_name_lower", table_name="users")
    op.drop_column("users", "display_name")
