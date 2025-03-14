from middleware.third_party_interaction_logic.github_issue_api_logic import (
    get_github_issue_project_statuses,
    get_project_id,
    get_repository_id,
    create_issue,
)


def test_get_github_issue_project_statuses():
    gipi = get_github_issue_project_statuses(issue_numbers=[5, 18])

    print(gipi)


def test_get_project_id():
    print(get_project_id())


def test_get_repository_id():
    print(get_repository_id())


def test_create_issue():
    result = create_issue(
        title="Test title",
        body="Test body",
    )

    print(result)
