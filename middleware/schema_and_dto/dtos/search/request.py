from typing import Optional

from pydantic import Field

from middleware.enums import OutputFormatEnum
from middleware.schema_and_dto.dtos.search.base import SearchFollowRequestBaseDTO
from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum


class SearchRequestsDTO(SearchFollowRequestBaseDTO):
    location_id: int = Field(
        description="The id of the location.",
        json_schema_extra=MetadataInfo(source=SourceMappingEnum.QUERY_ARGS),
    )
    output_format: Optional[OutputFormatEnum] = None
