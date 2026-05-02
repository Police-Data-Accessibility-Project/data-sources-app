from typing import Optional

from middleware.third_party_interaction_logic.github.constants import (
    GH_ORG_NAME,
    GH_REPO_NAME,
)
from middleware.third_party_interaction_logic.github.helpers import make_graph_ql_query


class GithubLabelManager:
    def __init__(self):
        self.label_name_to_id = self.get_labels()

    @staticmethod
    def _build_labels_query(after: Optional[str] = None) -> str:
        after_arg = f', after: "{after}"' if after is not None else ""
        return """
        query {
          repository(owner: "%s", name: "%s") {
            labels(first: 100%s) {
              pageInfo {
                endCursor
                hasNextPage
              }
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
            after_arg,
        )

    def get_labels(self) -> dict[str, str]:
        """Fetch all repository labels, following GraphQL cursor pagination.

        GitHub's GraphQL API caps ``first`` at 100, so we must follow
        ``pageInfo.endCursor`` until ``hasNextPage`` is false to retrieve
        every label. See issue #675.
        """
        d: dict[str, str] = {}
        after: Optional[str] = None
        while True:
            query = self._build_labels_query(after=after)
            response = make_graph_ql_query(query=query)
            labels_payload = response["data"]["repository"]["labels"]
            for label in labels_payload["nodes"]:
                d[label["name"]] = label["id"]

            page_info = labels_payload.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                break
            after = page_info.get("endCursor")
            if after is None:
                break

        return d
