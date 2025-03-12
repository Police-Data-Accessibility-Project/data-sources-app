from middleware.third_party_interaction_logic.github_issue_api_logic import (
    get_github_issue_project_statuses,
    create_github_issue,
)


def test_get_github_issue_project_statuses():
    # https://github.com/Police-Data-Accessibility-Project/data-requests/issues/3

    results = get_github_issue_project_statuses(issue_numbers=[3])
    print(results)


def test_create_github_issue():
    create_github_issue(title="Testing", body="Testing Body")
