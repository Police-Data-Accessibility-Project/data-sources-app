from github import Github
from github import Auth

from middleware.util import get_env_variable


def create_github_issue(title: str, body: str) -> str:
    """
    Create a github issue and return its url
    :param title: The title of the issue
    :param body: The body of the issue
    :return:
    """
    auth = Auth.Token(
        get_env_variable("GH_API_ACCESS_TOKEN")
    )

    g = Github(auth=auth)

    repo = g.get_repo(get_env_variable("GH_ISSUE_REPO_NAME"))
    issue = repo.create_issue(title=title, body=body)

    return issue.url