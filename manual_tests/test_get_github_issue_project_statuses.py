from middleware.third_party_interaction_logic.github_issue_api_logic import (
    get_github_issue_project_statuses,
    get_project_id,
    get_repository_id,
    create_issue,
    assign_issue_to_project,
    get_project_status_field,
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


def test_assign_issue_to_project():
    response = assign_issue_to_project("I_kwDOLzuDQM6uDIHs")
    print(response)


def test_get_project_fields():
    response = get_project_status_field()
    print(response)
