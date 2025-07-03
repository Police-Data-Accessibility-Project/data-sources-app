from pydantic import BaseModel

from middleware.third_party_interaction_logic.github.issue_info import GithubIssueInfo


class SynchronizeTestInfo(BaseModel):
    data_request_id: int
    github_issue_info: GithubIssueInfo
