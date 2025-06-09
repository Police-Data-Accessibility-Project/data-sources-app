from pydantic import BaseModel


class RefreshSessionRequestDTO(BaseModel):
    refresh_token: str
