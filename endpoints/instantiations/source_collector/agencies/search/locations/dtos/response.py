from pydantic import BaseModel, Field

from middleware.schema_and_dto.dtos._helpers import default_field_required
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import MetadataInfo
from utilities.enums import SourceMappingEnum


class InnerSearchLocationResponse(BaseModel):
    agency_id: int = default_field_required(
        description="The ID of the agency.",
    )
    similarity: float = Field(
        ...,
        description="The similarity of the agency to the search.",
        ge=0,
        le=1,
        json_schema_extra=MetadataInfo(
            required=False,
            source=SourceMappingEnum.JSON
        )
    )

class SearchLocationRequestResponse(BaseModel):
    request_id: int = default_field_required(
        description="The ID of the request.",
    )
    results: list[InnerSearchLocationResponse] = default_field_required(
        description="The results of the search.",
    )

class SourceCollectorAgencySearchLocationResponseDTO(BaseModel):
    responses: list[SearchLocationRequestResponse] = default_field_required(
        description="The responses of the search.",
    )