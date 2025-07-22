import datetime
from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum


class SourceCollectorSyncAgenciesRequestDTO(BaseModel):
    page: int = Field(  # pyright: ignore [reportUnknownVariableType]
        default=1,
        description="The page number to retrieve",
        json_schema_extra=MetadataInfo(
            required=False, source=SourceMappingEnum.QUERY_ARGS
        ),
    )
    updated_at: Optional[datetime.date] = Field(  # pyright: ignore [reportUnknownVariableType]
        default=None,
        description="The date to filter by",
        json_schema_extra=MetadataInfo(
            required=False, source=SourceMappingEnum.QUERY_ARGS
        ),
    )
