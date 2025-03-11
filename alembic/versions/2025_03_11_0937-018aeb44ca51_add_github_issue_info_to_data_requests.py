"""Add Github issue info to data requests

Revision ID: 018aeb44ca51
Revises: e8897f1ae7fb
Create Date: 2025-03-11 09:37:32.876991

"""

import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "018aeb44ca51"
down_revision: Union[str, None] = "e8897f1ae7fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "data_requests_github_issue_info_github_issue_url_key",
        table_name="data_requests_github_issue_info",
        type_="unique",
    )
    op.drop_constraint(
        "data_requests_github_issue_info_github_issue_number_key",
        table_name="data_requests_github_issue_info",
        type_="unique",
    )

    ids_and_issue_urls = [
        [
            "124",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/93",
        ],
        [
            "121",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/92",
        ],
        [
            "123",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/91",
        ],
        [
            "122",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/90",
        ],
        [
            "119",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/86",
        ],
        [
            "42",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "60",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "61",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "62",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "63",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "68",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "65",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "93",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "106",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "103",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "102",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/240",
        ],
        [
            "100",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/13",
        ],
        [
            "95",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/12",
        ],
        [
            "96",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/18",
        ],
        [
            "99",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/19",
        ],
        [
            "90",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/16",
        ],
        [
            "91",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/17",
        ],
        [
            "30",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/206",
        ],
        [
            "120",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/89",
        ],
        [
            "6",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/25",
        ],
        [
            "116",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/6",
        ],
        [
            "53",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/44",
        ],
        [
            "113",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/63",
        ],
        [
            "115",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/64",
        ],
        [
            "111",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/62",
        ],
        [
            "98",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/57",
        ],
        [
            "105",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/60",
        ],
        [
            "101",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/58",
        ],
        [
            "31",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/33",
        ],
        [
            "24",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/30",
        ],
        [
            "19",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/28",
        ],
        [
            "59",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/49",
        ],
        [
            "39",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/36",
        ],
        [
            "1",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/22",
        ],
        [
            "2",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/21",
        ],
        [
            "57",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/47",
        ],
        [
            "75",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/56",
        ],
        [
            "74",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/55",
        ],
        [
            "73",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/54",
        ],
        [
            "71",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/53",
        ],
        [
            "69",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/52",
        ],
        [
            "67",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/52",
        ],
        [
            "66",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/51",
        ],
        [
            "64",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/50",
        ],
        [
            "58",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/48",
        ],
        [
            "55",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/46",
        ],
        [
            "54",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/45",
        ],
        [
            "49",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/42",
        ],
        [
            "50",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/10",
        ],
        [
            "38",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/35",
        ],
        [
            "46",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/41",
        ],
        [
            "45",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/40",
        ],
        [
            "41",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/38",
        ],
        [
            "44",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/39",
        ],
        [
            "40",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/37",
        ],
        [
            "37",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/34",
        ],
        [
            "23",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/29",
        ],
        [
            "27",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/32",
        ],
        [
            "10",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/20",
        ],
        [
            "4",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/23",
        ],
        [
            "5",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/24",
        ],
        [
            "7",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/26",
        ],
        [
            "8",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/27",
        ],
        [
            "3",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/20",
        ],
        [
            "56",
            "https://github.com/Police-Data-Accessibility-Project/scrapers/issues/239",
        ],
        [
            "118",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/7",
        ],
        [
            "114",
            "https://github.com/Police-Data-Accessibility-Project/data-projects/issues/3",
        ],
    ]
    for data_request_id, url in ids_and_issue_urls:
        issue_number = int(re.match(r".*issues/(\d+)", url).group(1))
        op.execute(
            f"""
        INSERT INTO data_requests_github_issue_info (data_request_id, github_issue_url, github_issue_number)
            SELECT {data_request_id}, '{url}', {issue_number}
            WHERE EXISTS (
                SELECT 1
                FROM DATA_REQUESTS
                WHERE ID = {data_request_id}
            );
        """
        )


def downgrade() -> None:
    op.create_unique_constraint(
        "data_requests_github_issue_info_github_issue_number_key",
        table_name="data_requests_github_issue_info",
        columns=["github_issue_number"],
    )
    op.create_unique_constraint(
        "data_requests_github_issue_info_github_issue_url_key",
        table_name="data_requests_github_issue_info",
        columns=["github_issue_url"],
    )
