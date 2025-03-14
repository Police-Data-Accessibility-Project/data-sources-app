import re
from typing import Optional

from github import Github
from github import Auth
import requests
from pydantic import BaseModel

from database_client.enums import RequestStatus
from middleware.util import get_env_variable
from dataclasses import dataclass


class GithubIssueInfo(BaseModel):
    url: str
    number: int
    data_request_id: Optional[int] = None


def create_github_issue(title: str, body: str) -> GithubIssueInfo:
    """
    Create a github issue and return its url
    :param title: The title of the issue
    :param body: The body of the issue
    :return:
    """
    auth = Auth.Token(get_env_variable("GH_API_ACCESS_TOKEN"))

    g = Github(auth=auth)
    repo_owner = get_env_variable("GH_ISSUE_REPO_OWNER")
    repo_name = get_env_variable("GH_ISSUE_REPO_NAME")

    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    issue = repo.create_issue(title=title, body=body)

    return GithubIssueInfo(url=issue.url, number=issue.number)


class GithubIssueProjectInfo:

    def __init__(self):
        self.d: dict[int, str] = {}

    def add_project_status(self, issue_number: int, project_status: str):
        if issue_number in self.d:
            if self.d[issue_number] == project_status:
                return
            raise ValueError(
                f"Issue number with conflicting status {issue_number}: {project_status} vs {self.d[issue_number]}"
            )
        self.d[issue_number] = project_status

    def get_project_status(self, issue_number: int) -> RequestStatus:
        try:
            return RequestStatus(self.d[issue_number])
        except KeyError:
            raise ValueError(f"Unknown issue number {issue_number}")


def get_project_id():
    query = """
    query {
      organization(login: "Police-Data-Accessibility-Project") {
        projectV2(number: 26) {  # Specific project number
          id
        }
      }
    }
    """
    response = make_graph_ql_query(query=query)
    return response["data"]["organization"]["projectV2"]["id"]


def get_repository_id():
    query = """
    query FindRepo {
      repository(owner: "Police-Data-Accessibility-Project", name: "data-requests") {
        id
      }
    }
    """
    response = make_graph_ql_query(query=query)
    return response["data"]["repository"]["id"]


class GithubIssueInfo(BaseModel):
    issue: int
    id: str


def create_issue(title: str, body: str) -> GithubIssueInfo:
    query = """
    mutation CreateIssue {
        createIssue(input: {
          repositoryId: "%s",
          title: "%s", 
          body: "%s"
        }
      ) {
      issue {
            number,
            id
          }
        }
      }
    """ % (
        get_env_variable("GH_REPO_ID"),
        title,
        body,
    )
    response = make_graph_ql_query(query=query)
    data = response["data"]
    issue = data["createIssue"]["issue"]
    return GithubIssueInfo(issue=issue["number"], id=issue["id"])


def assign_issue_to_project(issue_id: str):
    query = """
    mutation AssignIssueToProject {
        addProjectV2ItemById(
            input: {
                projectId: "%s",
                contentId: "%s"
            }
        ) 
    {
        item {
          id
        }
      }
    }
    """ % (
        get_env_variable("GH_PROJECT_ID"),
        issue_id,
    )
    return make_graph_ql_query(query=query)


def get_project_status_field():
    query = """
    query {
      node(id: "%s") {
        ... on ProjectV2 {
          id
          title
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field {
                id
                name
                dataType
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                dataType
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """ % get_env_variable(
        "GH_PROJECT_ID"
    )
    response = make_graph_ql_query(query=query)
    data = response["data"]
    project = data["node"]
    fields = project["fields"]
    nodes = fields["nodes"]
    for node in nodes:
        if node["name"] == "Status":
            return node


def generate_issues_and_project_get_graphql_query():
    return """
    query {
      organization(login: "Police-Data-Accessibility-Project") {
        projectV2(number: 26) {  # Specific project number
          title
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  number
                  title
                }
              }
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
              }
            }
          }
        }
      }
    }
    """


def convert_graph_ql_result_to_issue_info(result: dict):
    gipi = GithubIssueProjectInfo()
    data = result.get("data")
    organization = data.get("organization")
    project_v2 = organization.get("projectV2")
    items = project_v2.get("items")
    nodes = items.get("nodes")
    for node in nodes:
        issue_number = node.get("content").get("number")
        project_status = node.get("fieldValueByName").get("name")

        gipi.add_project_status(
            issue_number=issue_number, project_status=project_status
        )

    return gipi


def get_github_issue_project_statuses(
    issue_numbers: list[int],
) -> GithubIssueProjectInfo:

    query = generate_issues_and_project_get_graphql_query()

    response = make_graph_ql_query(query=query)

    gipi = convert_graph_ql_result_to_issue_info(response)

    return gipi


def make_graph_ql_query(query: str):
    access_token = get_env_variable("GH_API_ACCESS_TOKEN")
    response = requests.post(
        url="https://api.github.com/graphql",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={"query": query},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
