"""Update github issue info for select data requests

Revision ID: 9687740397b7
Revises: 7bcc381f0344
Create Date: 2025-03-13 15:14:17.484915

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9687740397b7"
down_revision: Union[str, None] = "7bcc381f0344"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    list_ = [
        [
            206,
            "https://github.com/Police-Data-Accessibility-Project/data-requests/issues/97",
            97,
        ],
        [
            239,
            "https://github.com/Police-Data-Accessibility-Project/data-requests/issues/96",
            96,
        ],
        [
            240,
            "https://github.com/Police-Data-Accessibility-Project/data-requests/issues/98",
            98,
        ],
    ]
    for old_issue_number, new_issue_url, new_issue_number in list_:
        op.execute(
            sa.text(
                """
            UPDATE data_requests_github_issue_info SET 
            github_issue_url=:new_issue_url, 
            github_issue_number=:new_issue_number
            WHERE github_issue_number=:old_issue_number"""
            ).bindparams(
                new_issue_url=new_issue_url,
                new_issue_number=new_issue_number,
                old_issue_number=old_issue_number,
            )
        )


def downgrade() -> None:
    # This action cannot be reversed
    pass
