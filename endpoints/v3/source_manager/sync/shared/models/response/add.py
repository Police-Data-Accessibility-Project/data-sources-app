from pydantic import BaseModel, Field


class SourceManagerSyncAddInnerResponse(BaseModel):
    request_id: int = Field(
        description="The identity of the entity in the request. Corresponds to an ID in the Source Manager database."
    )
    app_id: int = Field(description="The identity of the entity in the app database.")


class SourceManagerSyncAddOuterResponse(BaseModel):
    entities: list[SourceManagerSyncAddInnerResponse]
