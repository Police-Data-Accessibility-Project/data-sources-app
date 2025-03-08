"""Enhance followed searches

Revision ID: fb808b640a3f
Revises: e628c1173d56
Create Date: 2025-03-07 07:38:15.206500

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fb808b640a3f"
down_revision: Union[str, None] = "e628c1173d56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add category_id to followed searches
    op.add_column(
        table_name="link_user_followed_location",
        column=sa.Column("category_id", sa.Integer, nullable=True),
    )
    # Add foreign key constraint
    op.create_foreign_key(
        "fk_link_user_followed_location_category_id",
        source_table="link_user_followed_location",
        referent_table="record_categories",
        local_cols=["category_id"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    # Remove category_id from followed searches
    op.drop_column(table_name="link_user_followed_location", column_name="category_id")
