from middleware.third_party_interaction_logic.github.constants import (
    GH_ORG_NAME,
    GH_REPO_NAME,
)
from middleware.third_party_interaction_logic.github.helpers import make_graph_ql_query


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
