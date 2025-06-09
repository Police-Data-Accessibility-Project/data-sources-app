from pydantic import BaseModel


class GithubIssueURLInfosDTO(BaseModel):
    github_issue_url: str
    data_request_id: int
