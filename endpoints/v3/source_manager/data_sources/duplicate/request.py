from pydantic import BaseModel, Field


class SourceManagerDataSourcesDuplicateRequest(BaseModel):
    urls: list[str] = Field(
        description="A list of URLs to check for duplicates.",
    )
