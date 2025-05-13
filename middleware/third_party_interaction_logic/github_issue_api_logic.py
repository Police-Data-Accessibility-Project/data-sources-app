import json
import re
from typing import Optional

from github import Github
from github import Auth
import requests
from pydantic import BaseModel

from database_client.enums import RequestStatus
from middleware.enums import RecordTypes
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

    def get_all_ids(self):
        return list(self.d.values())


class GIPIInfo(BaseModel):
    project_status: str
    record_types: list[RecordTypes]

    def record_types_as_list_of_strings(self) -> list[str]:
        return [record_type.value for record_type in self.record_types]


class GithubIssueProjectInfo:

    def __init__(self):
        self.issue_number_to_info: dict[int, GIPIInfo] = {}

    def add_info(self, issue_number: int, gipi_info: GIPIInfo):
        if issue_number in self.issue_number_to_info:
            if (
                self.issue_number_to_info[issue_number].project_status
                == gipi_info.project_status
            ):
                return
            raise ValueError(
                f"Issue number with conflicting status {issue_number}: "
                f"{gipi_info.project_status} vs {self.issue_number_to_info[issue_number]}"
            )
        self.issue_number_to_info[issue_number] = gipi_info

    def get_info(self, issue_number: int) -> GIPIInfo:
        return self.issue_number_to_info[issue_number]

    def get_project_status(self, issue_number: int) -> RequestStatus:
        try:
            gipi_info = self.issue_number_to_info[issue_number]
            return RequestStatus(gipi_info.project_status)
        except KeyError:
            raise ValueError(f"Unknown issue number {issue_number}")

    def get_labels(self, issue_number: int) -> list[str]:
        try:
            gipi_info = self.issue_number_to_info[issue_number]
            return gipi_info.record_types
        except KeyError:
            raise ValueError(f"Unknown issue number {issue_number}")


GH_PROJECT_NUMBER = 26
GH_ORG_NAME = "Police-Data-Accessibility-Project"
GH_REPO_NAME = "data-requests"


class GithubLabelManager:

    def __init__(self):
        self.label_name_to_id = self.get_labels()

    def get_labels(self):
        query = """
        query {
          repository(owner: "%s", name: "%s") {
            labels(first: 100) {
              nodes {
                id
                name
              }
            }
          }
        }
        """ % (
            GH_ORG_NAME,
            GH_REPO_NAME,
        )
        response = make_graph_ql_query(query=query)
        labels = response["data"]["repository"]["labels"]["nodes"]
        d = {}
        for label in labels:
            d[label["name"]] = label["id"]
        return d


class GithubIssueManager:

    def __init__(self):
        self.project_id = self.get_project_id()
        self.repo_id = self.get_repository_id()
        node = self.get_project_status_field()
        self.project_status_field_id = node["id"]
        self.project_status_manager = ProjectStatusManager(node["options"])
        self.label_manager = GithubLabelManager()

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

    def get_record_type_label_ids(self, record_types: list[RecordTypes]):
        record_type_str_list = [
            f"RT-{record_type.value}" for record_type in record_types
        ]
        return [
            self.label_manager.label_name_to_id[record_type_str]
            for record_type_str in record_type_str_list
        ]

    def create_issue(
        self, title: str, body: str, record_types: list[RecordTypes]
    ) -> GithubIssueInfo:
        label_ids = self.get_record_type_label_ids(record_types)
        query = """
        mutation CreateIssue {
            createIssue(input: {
              repositoryId: "%s",
              title: %s, 
              body: %s,
              labelIds: %s
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
            json.dumps(title),
            json.dumps(body),
            json.dumps(label_ids),
        )
        response = make_graph_ql_query(query=query)
        try:
            data = response["data"]
        except KeyError:
            raise ValueError(f"Failed to create issue: {response}")
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
        self,
        title: str,
        body: str,
        status: RequestStatus,
        record_types: list[RecordTypes],
    ) -> GithubIssueInfo:
        gii: GithubIssueInfo = self.create_issue(
            title=title, body=body, record_types=record_types
        )
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


def get_issue_project_statii_and_labels(global_ids: list[str]):
    issue_subqueries = []
    for global_issue_id in global_ids:
        issue_subquery = f"""
        issue{global_issue_id}: node(id: {global_issue_id}) {{
            ... on Issue {{
              number
              title
              labels(first: 10) {{   # Fetching issue labels
                nodes {{
                  name
                }}
              }}            
            }}
        }}
        """
        issue_subqueries.append(issue_subquery)

    query = f"""
      query{{
               {"\n".join(issue_subqueries)}
        }}
    """
    response = make_graph_ql_query(query=query)
    return response


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
                  labels(first: 10) {   # Fetching issue labels
                    nodes {
                      name
                    }
                  }
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
        label_nodes = node.get("content").get("labels").get("nodes")
        record_types = []
        for label_node in label_nodes:
            if "RT-" in label_node.get("name"):
                record_type_name = re.sub("RT-", "", label_node.get("name"))
                record_types.append(record_type_name)
        gipi_info = GIPIInfo(project_status=project_status, record_types=record_types)

        gipi.add_info(issue_number=issue_number, gipi_info=gipi_info)

    return gipi


def get_github_issue_project_statuses(
    issue_numbers: list[int],
) -> GithubIssueProjectInfo:
    query = generate_issues_and_project_get_graphql_query()

    response = make_graph_ql_query(query=query)

    gipi = convert_graph_ql_result_to_issue_info(response)

    return gipi


def make_graph_ql_query(query: str, variables: Optional[dict] = None):
    access_token = get_env_variable("GH_API_ACCESS_TOKEN")
    response = requests.post(
        url="https://api.github.com/graphql",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "query": query,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
