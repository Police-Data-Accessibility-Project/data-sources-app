import os
import json
import requests


def post_comment(issue_number, repo_token, message):
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
