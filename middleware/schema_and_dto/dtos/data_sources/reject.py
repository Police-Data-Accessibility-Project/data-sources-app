from pydantic import BaseModel


class DataSourcesRejectDTO(BaseModel):
    resource_id: int
    rejection_note: str
