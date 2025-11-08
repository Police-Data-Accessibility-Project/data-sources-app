from pydantic import BaseModel


class MetaURLSyncContentModel(BaseModel):
    url: str
    agency_id: int
