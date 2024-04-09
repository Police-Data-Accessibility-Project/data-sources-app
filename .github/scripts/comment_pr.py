import os
import json
import requests


def post_comment(issue_number: str, repo_token: str, message: str):
    """
    :param issue_number: The number of the issue to which the comment will be posted.
    :param repo_token: The access token required to authorize the request to the GitHub API.
    :param message: The body of the comment to be posted.
    :return: None

    This method posts a comment to a specific GitHub issue identified by `issue_number`.
    The comment is created using the provided `message`. The `repo_token` is necessary to authorize the
    * request to the GitHub API.

    Raises:
        requests.HTTPError: If the request to the GitHub API fails for any reason.
    """
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {repo_token}"}
    data = {"body": message}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()


issue_number = os.getenv("GITHUB_REF").split("/")[-2]
repo_token = os.getenv("GITHUB_TOKEN")

# Assume you've saved the outputs to files
mypy_result = open("mypy_output.txt").read().strip()
pydocstyle_result = open("pydocstyle_output.txt").read().strip()

comment = f"## Type Hinting and Docstring Checks\n\n### mypy\n```\n{mypy_result}\n```\n### pydocstyle\n```\n{pydocstyle_result}\n```"
post_comment(issue_number, repo_token, comment)
