from pydantic import BaseModel, Field


class ExternalAccountsModel(BaseModel):
    github: str | None = Field(
        description="The GitHub username of the user.",
    )
