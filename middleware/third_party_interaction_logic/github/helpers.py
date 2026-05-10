import re
from typing import Optional, Union

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


def generate_issues_and_project_get_graphql_query(after: Optional[str] = None) -> str:
    """Build the GraphQL query for fetching project items.

    When ``after`` is provided, the query will request the page of items
    following the given cursor; otherwise the first page is requested.
    """
    after_arg = f', after: "{after}"' if after is not None else ""
    return f"""
    query {{
      organization(login: "Police-Data-Accessibility-Project") {{
        projectV2(number: 26) {{
          title
          items(first: 100{after_arg}) {{
            pageInfo {{
              endCursor
              hasNextPage
            }}
            nodes {{
              content {{
                ... on Issue {{
                  number
                  title
                  labels(first: 10) {{
                    nodes {{
                      name
                    }}
                  }}
                }}
              }}
              fieldValueByName(name: "Status") {{
                ... on ProjectV2ItemFieldSingleSelectValue {{
                  name
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """


def _extract_items(result: dict) -> dict:
    data = result.get("data")
    if data is None:
        raise ValueError("No data in result")
    organization = data.get("organization")
    project_v2 = organization.get("projectV2")
    return project_v2.get("items")


def convert_graph_ql_result_to_issue_info(
    result: Union[dict, list[dict]],
) -> GithubIssueProjectInfo:
    """Convert one or more project-items response payloads into a
    ``GithubIssueProjectInfo`` instance.

    Accepts either a single response dict (single page) or a list of response
    dicts (paginated calls), merging all nodes into the result.
    """
    pages: list[dict] = result if isinstance(result, list) else [result]
    gipi = GithubIssueProjectInfo()
    for page in pages:
        items = _extract_items(page)
        nodes = items.get("nodes") or []
        for node in nodes:
            issue_number = node.get("content").get("number")
            project_status = node.get("fieldValueByName").get("name")
            label_nodes = node.get("content").get("labels").get("nodes")
            record_types = []
            for label_node in label_nodes:
                if "RT-" in label_node.get("name"):
                    record_type_name = re.sub("RT-", "", label_node.get("name"))
                    record_types.append(record_type_name)
            gipi_info = GIPIInfo(
                project_status=project_status, record_types=record_types
            )

            gipi.add_info(issue_number=issue_number, gipi_info=gipi_info)

    return gipi


def get_github_issue_project_statuses(
    issue_numbers: list[int],
) -> GithubIssueProjectInfo:
    """Fetch project statuses for issues, following GraphQL cursor pagination.

    GitHub's GraphQL API caps ``first`` at 100, so for projects with more than
    100 items we must follow the ``pageInfo.endCursor`` cursor until
    ``hasNextPage`` is false. See issue #675.
    """
    pages: list[dict] = []
    after: Optional[str] = None
    while True:
        query = generate_issues_and_project_get_graphql_query(after=after)
        response = make_graph_ql_query(query=query)
        pages.append(response)

        items = _extract_items(response)
        page_info = items.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if after is None:
            break

    return convert_graph_ql_result_to_issue_info(pages)


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
