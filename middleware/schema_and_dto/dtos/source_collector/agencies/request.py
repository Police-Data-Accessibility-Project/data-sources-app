import datetime

from pydantic import BaseModel, Field

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum


class SourceCollectorSyncAgenciesRequestDTO(BaseModel):
    page: int = Field(
        default=1,
        description="The page number to retrieve",
        json_schema_extra=MetadataInfo(
            required=False, source=SourceMappingEnum.QUERY_ARGS
        ),
    )
    updated_at: datetime.date = Field(
        default=None,
        description="The date to filter by",
        json_schema_extra=MetadataInfo(
            required=False, source=SourceMappingEnum.QUERY_ARGS
        ),
    )
