import re
from typing import Optional

import requests

from middleware.third_party_interaction_logic.github.issue_project_info.core import (
    GithubIssueProjectInfo,
)
from middleware.third_party_interaction_logic.github.issue_project_info.model import (
    GIPIInfo,
)
from middleware.util.env import get_env_variable


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
    if data is None:
        raise ValueError("No data in result")
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
