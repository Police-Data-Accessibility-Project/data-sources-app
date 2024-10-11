from middleware.third_party_interaction_logic.github_issue_api_logic import (
    create_github_issue,
)


def test_create_github_issue():
    github_user_info = create_github_issue(
        title="Test",
        body="Test body",
    )
    print(github_user_info)
