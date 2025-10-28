from pydantic import BaseModel, Field


class UpdateMetaURLsInnerRequest(BaseModel):
    app_id: int

    url: str


class UpdateMetaURLsOuterRequest(BaseModel):
    meta_urls: list[UpdateMetaURLsInnerRequest] = Field(max_length=1000)
