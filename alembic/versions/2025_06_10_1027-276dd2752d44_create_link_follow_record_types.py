"""Create link_follow_record_types

Revision ID: 276dd2752d44
Revises: 8f26c4cc4c35
Create Date: 2025-06-10 10:27:25.247301

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from middleware.alembic_helpers import id_column, record_type_id_column

# revision identifiers, used by Alembic.
revision: str = "276dd2752d44"
down_revision: Union[str, None] = "8f26c4cc4c35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "link_follow_record_types"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        id_column(),
        sa.Column(
            "follow_id",
            sa.Integer,
            sa.ForeignKey("link_user_followed_location.id", ondelete="CASCADE"),
            nullable=False,
        ),
        record_type_id_column(),
        sa.UniqueConstraint(
            "follow_id",
            "record_type_id",
            name="link_follow_record_types_follow_id_record_type_id_key",
        ),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
