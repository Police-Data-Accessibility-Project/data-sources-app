from pydantic import BaseModel, Field


class SourceManagerDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1, description="IDs to delete.")
