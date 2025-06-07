from pydantic import BaseModel


class LoginWithGithubRequestDTO(BaseModel):
    gh_access_token: str
