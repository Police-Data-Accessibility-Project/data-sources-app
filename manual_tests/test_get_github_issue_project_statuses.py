from database_client.enums import RequestStatus
from middleware.third_party_interaction_logic.github_issue_api_logic import (
    get_github_issue_project_statuses,
    create_github_issue, GithubIssueManager,
)


def test_get_github_issue_project_statuses():
    # https://github.com/Police-Data-Accessibility-Project/data-requests/issues/3

    results = get_github_issue_project_statuses(issue_numbers=[3])
    print(results)


def test_create_github_issue():
    create_github_issue(title="Testing", body="Testing Body")

def test_github_issue_manager():
    gim = GithubIssueManager()
    gim.create_issue_with_status(
        title="test",
        body="test body",
        status=RequestStatus.READY_TO_START
    )
