"""Remove relation_column and column_permission tables

Revision ID: 59a0070a8a83
Revises: 89b4dbcb8827
Create Date: 2025-02-27 15:53:22.901082

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "59a0070a8a83"
down_revision: Union[str, None] = "89b4dbcb8827"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

relation_role_enum = sa.Enum(
    "STANDARD",
    "OWNER",
    "ADMIN",
    name="relation_role",
)
access_permission_enum = sa.Enum(
    "READ",
    "WRITE",
    "NONE",
    name="access_permission",
)


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS relation_column_permission_view")
    op.drop_table("column_permission")
    op.drop_table("relation_column")

    relation_role_enum.drop(op.get_bind())
    access_permission_enum.drop(op.get_bind())


def downgrade() -> None:
    op.create_table(
        "relation_column",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("relation", sa.Text(), nullable=False),
        sa.Column("associated_column", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="relation_column_pkey"),
        sa.UniqueConstraint(
            "relation", "associated_column", name="unique_relation_column"
        ),
    )

    op.create_table(
        "column_permission",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("rc_id", sa.Integer(), nullable=False),
        sa.Column("relation_role", relation_role_enum, nullable=False),
        sa.Column("access_permission", access_permission_enum, nullable=False),
        sa.PrimaryKeyConstraint("id", name="column_permission_pkey"),
        sa.UniqueConstraint("rc_id", "relation_role", name="unique_column_permission"),
        sa.ForeignKeyConstraint(
            ["rc_id"],
            ["relation_column.id"],
            ondelete="CASCADE",
            name="column_permission_rc_id_fkey",
        ),
    )

    op.execute(
        """
    CREATE OR REPLACE VIEW public.relation_column_permission_view
     AS
     SELECT rc.relation,
        rc.associated_column,
        cp.relation_role,
        cp.access_permission
       FROM relation_column rc
         LEFT JOIN column_permission cp ON cp.rc_id = rc.id;
    """
    )
