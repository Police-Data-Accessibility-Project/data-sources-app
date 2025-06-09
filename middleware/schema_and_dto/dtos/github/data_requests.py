from pydantic import BaseModel


class GithubDataRequestsIssuesPostDTO(BaseModel):
    data_request_id: int
