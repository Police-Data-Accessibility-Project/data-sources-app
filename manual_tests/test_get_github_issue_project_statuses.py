from middleware.third_party_interaction_logic.github_issue_api_logic import (
    get_github_issue_project_statuses,
)


def test_get_github_issue_project_statuses():
    gipi = get_github_issue_project_statuses(issue_numbers=[5, 18])

    print(gipi)
