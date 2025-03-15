from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.github_issue_app_logic import (
    synchronize_github_issues_with_data_requests,
)


def test_synchronize_manual():

    # Automatically starts the Synchronize Process
    synchronize_github_issues_with_data_requests(
        db_client=DatabaseClient(), access_info=None
    )
