from typing import Optional

from github import Github
from github import Auth
import requests
from pydantic import BaseModel

from database_client.enums import RequestStatus
from middleware.util import get_env_variable


class GithubIssueInfo(BaseModel):
    id: str
    url: str
    number: int
    data_request_id: Optional[int] = None


class ProjectStatusManager:

    def __init__(self, options: dict):
        self.d = {}
        for option in options:
            id_ = option["id"]
            name = option["name"]
            self.d[name] = id_

    def get_id(self, name):
        return self.d[name]


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


GH_PROJECT_NUMBER = 26
GH_ORG_NAME = "Police-Data-Accessibility-Project"
GH_REPO_NAME = "data-requests"


class GithubIssueManager:

    def __init__(self):
        self.project_id = self.get_project_id()
        self.repo_id = self.get_repository_id()
        node = self.get_project_status_field()
        self.project_status_field_id = node["id"]
        self.project_status_manager = ProjectStatusManager(node["options"])

    def get_project_id(self):
        query = """
        query {
          organization(login: "%s") {
            projectV2(number: %s) {
              id
            }
          }
        }
        """ % (
            GH_ORG_NAME,
            GH_PROJECT_NUMBER,
        )
        response = make_graph_ql_query(query=query)
        return response["data"]["organization"]["projectV2"]["id"]

    def get_repository_id(self):
        query = """
        query FindRepo {
          repository(owner: "%s", name: "%s") {
            id
          }
        }
        """ % (
            GH_ORG_NAME,
            GH_REPO_NAME,
        )
        response = make_graph_ql_query(query=query)
        return response["data"]["repository"]["id"]

    def create_issue(self, title: str, body: str) -> GithubIssueInfo:
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
                id,
                url
              }
            }
          }
        """ % (
            self.repo_id,
            title,
            body,
        )
        response = make_graph_ql_query(query=query)
        data = response["data"]
        issue = data["createIssue"]["issue"]
        return GithubIssueInfo(url=issue["url"], number=issue["number"], id=issue["id"])

    def assign_status(self, project_item_id: str, status: RequestStatus):
        option_id = self.project_status_manager.get_id(status.value)

        query = """
        mutation {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: "%s",
              itemId: "%s",
              fieldId: "%s",
              value: {
                singleSelectOptionId: "%s"
              }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """ % (
            self.project_id,
            project_item_id,
            self.project_status_field_id,
            option_id,
        )
        response = make_graph_ql_query(query)
        return response

    def create_issue_with_status(
        self, title: str, body: str, status: RequestStatus
    ) -> GithubIssueInfo:
        gii: GithubIssueInfo = self.create_issue(title=title, body=body)
        project_item_id = self.assign_issue_to_project(gii.id)
        self.assign_status(project_item_id=project_item_id, status=status)
        return gii

    def assign_issue_to_project(self, issue_id: str) -> str:
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
            self.project_id,
            issue_id,
        )
        response = make_graph_ql_query(query=query)
        return response["data"]["addProjectV2ItemById"]["item"]["id"]

    def get_project_status_field(self):
        query = (
            """
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
        """
            % self.project_id
        )
        response = make_graph_ql_query(query=query)
        data = response["data"]
        project = data["node"]
        fields = project["fields"]
        nodes = fields["nodes"]
        for node in nodes:
            if node["name"] == "Status":
                return node


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
