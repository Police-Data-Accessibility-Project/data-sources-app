from typing import Optional

from pydantic import BaseModel


class GithubOAuthRequestDTO(BaseModel):
    redirect_url: Optional[str] = None
