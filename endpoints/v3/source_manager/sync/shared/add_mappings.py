from pydantic import BaseModel

from db.helpers_.url_mappings.mapper import URLMapper


class AddMappings(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    preexisting_url_mapper: URLMapper
    request_app_mappings: dict[int, int]
