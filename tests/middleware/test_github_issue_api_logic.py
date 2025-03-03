from middleware.primary_resource_logic.github_issue_app_logic import (
    get_github_issue_title,
    get_github_issue_body,
)


def test_get_github_issue_title_within_char_limit():

    result = get_github_issue_title(submission_notes="Test issue")
    assert result == "Test issue"


def test_get_github_issue_title_over_char_limit():

    result = get_github_issue_title(
        submission_notes="This is a test issue that is over 50 characters, and thus will be truncated in the title."
    )
    assert result == "This is a test issue that is over 50 characters, a..."


def test_get_github_issue_body():

    result = get_github_issue_body(
        submission_notes="Test issue", data_requirements="* Do x\n* Do y\n* Do z"
    )
    assert (
        result
        == """Submission Notes: Test issue

Data Requirements:
* Do x
* Do y
* Do z"""
    )
