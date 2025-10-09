from typing import Optional

from pydantic import BaseModel, Field

from middleware.enums import RecordTypes
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum, RecordCategoryEnum


class SearchRequestDTO(BaseModel):
    location_id: Optional[int] = Field(
        description="A location ID to search for data sources in.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.QUERY_ARGS, required=False
        ),
        default=None,
    )
    record_types: Optional[list[RecordTypes]] = Field(
        description="A record type to search for data sources in.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.QUERY_ARGS, required=False
        ),
        default=None,
    )
    record_categories: Optional[list[RecordCategoryEnum]] = Field(
        description="A record category to search for data sources in.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.QUERY_ARGS, required=False
        ),
        default=None,
    )
