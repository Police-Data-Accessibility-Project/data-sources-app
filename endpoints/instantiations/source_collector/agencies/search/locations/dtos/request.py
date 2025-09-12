from pydantic import BaseModel, Field

from middleware.schema_and_dto.dtos._helpers import default_field_required
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import MetadataInfo


class SourceCollectorAgencySearchLocationRequestInnerDTO(BaseModel):
    query: str = default_field_required(
        description="The query to search for agencies by location.",
    )
    iso: str = Field(
        description="The ISO code of the US State to search for agencies by location.",
        max_length=2,
        json_schema_extra=MetadataInfo(),
    )
    request_id: int = default_field_required(
        description="The request ID, used in identifying the response",
    )


class SourceCollectorAgencySearchLocationRequestDTO(BaseModel):
    requests: list[SourceCollectorAgencySearchLocationRequestInnerDTO] = (
        default_field_required(
            description="The list of requests to search for agencies by location.",
        )
    )
