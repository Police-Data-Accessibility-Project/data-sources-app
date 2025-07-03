import json

from db.enums import RequestStatus
from middleware.enums import RecordTypes
from middleware.third_party_interaction_logic.github.constants import (
    GH_ORG_NAME,
    GH_PROJECT_NUMBER,
    GH_REPO_NAME,
)
from middleware.third_party_interaction_logic.github.project_status_manager import (
    ProjectStatusManager,
)
from middleware.third_party_interaction_logic.github.issue_info import GithubIssueInfo
from middleware.third_party_interaction_logic.github.label_manager import (
    GithubLabelManager,
)
from middleware.third_party_interaction_logic.github.helpers import make_graph_ql_query


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

        raise ValueError("Status field not found")
