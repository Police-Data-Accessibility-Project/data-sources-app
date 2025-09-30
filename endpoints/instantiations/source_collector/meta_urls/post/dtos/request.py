from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class SourceCollectorMetaURLPostRequestInnerDTO(BaseModel):
    url: str = default_field_required(
        "The URL of the meta URL"
    )
    agency_id: int = default_field_required(
        "The ID of the agency"
    )

class SourceCollectorMetaURLPostRequestDTO(BaseModel):
    meta_urls: list[SourceCollectorMetaURLPostRequestInnerDTO] = default_field_required(
        "The list of meta URLs to add"
    )