from database_client.enums import RequestStatus
from middleware.enums import RecordTypes
from middleware.third_party_interaction_logic.github_issue_api_logic import (
    get_github_issue_project_statuses,
    GithubIssueManager,
    get_issue_project_statii_and_labels,
    GithubLabelManager,
)


def test_get_github_issue_project_statuses():
    # https://github.com/Police-Data-Accessibility-Project/data-requests/issues/3

    results = get_github_issue_project_statuses(issue_numbers=[115])
    print(results)


def test_github_issue_manager():
    gim = GithubIssueManager()
    pass


def test_create_issue_with_status():
    gim = GithubIssueManager()
    gim.create_issue_with_status(
        title="test",
        body="test",
        status=RequestStatus.READY_TO_START,
        record_types=[RecordTypes.ARREST_RECORDS, RecordTypes.PERSONNEL_RECORDS],
    )


def test_get_issue_project_statii_and_labels():
    get_issue_project_statii_and_labels(["f75ad846", "f75ad846"])


def test_github_label_manager():
    glm = GithubLabelManager()
    pass
