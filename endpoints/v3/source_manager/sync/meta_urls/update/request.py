from pydantic import BaseModel, Field

from endpoints.v3.source_manager.sync.meta_urls.shared.content import MetaURLSyncContentModel


class UpdateMetaURLsInnerRequest(BaseModel):
    app_id: int
    content: MetaURLSyncContentModel


class UpdateMetaURLsOuterRequest(BaseModel):
    meta_urls: list[UpdateMetaURLsInnerRequest] = Field(max_length=1000)
