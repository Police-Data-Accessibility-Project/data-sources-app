from typing import Optional

from pydantic import BaseModel


class GithubIssueInfo(BaseModel):
    id: str
    url: str
    number: int
    data_request_id: Optional[int] = None
