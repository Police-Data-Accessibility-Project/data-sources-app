from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.github_issue_app import (
    synchronize_github_issues_with_data_requests,
)
from middleware.util import get_env_variable


def test_synchronize_manual(monkeypatch):
    monkeypatch.setenv("DO_DATABASE_URL", get_env_variable("PROD_DATABASE_URL"))

    # Automatically starts the Synchronize Process
    synchronize_github_issues_with_data_requests(
        db_client=DatabaseClient(), access_info=None
    )
