import re

from github import Github
from github import Auth
import requests

from database_client.enums import RequestStatus
from middleware.util import get_env_variable
from dataclasses import dataclass

@dataclass
class GithubIssueInfo:
    url: str
    number: int


def create_github_issue(title: str, body: str) -> GithubIssueInfo:
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
    repo_name = get_env_variable("GH_ISSUE_REPO_NAME")
    repo_owner = get_env_variable("GH_ISSUE_REPO_OWNER")

    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    issue = repo.create_issue(title=title, body=body)

    return GithubIssueInfo(
        url=issue.url,
        number=issue.number
    )

class GithubIssueProjectInfo:

    def __init__(self):
        self.d = {}

    def add_project_status(self, issue_number: int, project_status: str):
        if issue_number in self.d:
            raise ValueError(f"Duplicate issue number {issue_number}")
        self.d[issue_number] = project_status

    def get_project_status(self, issue_number: int) -> RequestStatus:
        try:
            return RequestStatus(self.d[issue_number])
        except KeyError:
            raise ValueError(f"Unknown issue number {issue_number}")


def generate_graphql_query(issue_numbers: list[int]):
    issue_template = '''
    issue_{num}: issue(number: {num}) {{
      projectItems(first: 5) {{
        nodes {{
          status: fieldValueByName(name: "Status") {{
            ... on ProjectV2ItemFieldSingleSelectValue {{
              name
            }}
          }}
        }}
      }}
    }}'''

    issues = "\n".join([issue_template.format(num=issue_number) for issue_number in issue_numbers])

    owner = get_env_variable("GH_ISSUE_REPO_OWNER")
    repository_name = get_env_variable("GH_ISSUE_REPO_NAME")
    full_query = '''
    query {{
      repository(owner: "{owner}", name: "{repository_name}") {{
        {issues}
      }}
    }}'''.format(
        owner=owner,
        repository_name=repository_name,
        issues=issues
    )

    return full_query

def convert_graph_ql_result_to_issue_info(result: dict):
    gipi = GithubIssueProjectInfo()
    data = result.get("data")
    repository = data.get("repository")

    for issue_name, issue_info in repository.items():
        issue_number = re.match(r"issue_(\d+)", issue_name).group(1)

        project_items = issue_info.get("projectItems")
        nodes = project_items.get("nodes")
        for node in nodes:
            status = node.get("status")
            name = status.get("name")
            gipi.add_project_status(
                issue_number=issue_number,
                project_status=name
            )

    return gipi

def get_github_issue_project_statuses(
    issue_numbers: list[int]
) -> GithubIssueProjectInfo:

    query = generate_graphql_query(issue_numbers)

    token = get_env_variable("GH_API_ACCESS_TOKEN")

    response = requests.post(
        url="https://api.github.com/graphql",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={"query": query}
    )

    gipi = convert_graph_ql_result_to_issue_info(response.json())

    return gipi
