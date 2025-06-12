from db.enums import RequestStatus
from middleware.enums import RecordTypes
from middleware.third_party_interaction_logic.github.label_manager import (
    GithubLabelManager,
)
from middleware.third_party_interaction_logic.github.issue_manager import (
    GithubIssueManager,
)
from middleware.third_party_interaction_logic.github.helpers import (
    get_issue_project_statii_and_labels,
    get_github_issue_project_statuses,
)


def test_get_github_issue_project_statuses():
    # https://github.com/Police-Data-Accessibility-Project/data-requests/issues/3

    results = get_github_issue_project_statuses(issue_numbers=[115])
    print(results)
    print(results.issue_number_to_info)


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
