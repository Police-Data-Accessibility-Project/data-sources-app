from typing import Optional

from pydantic import BaseModel, Field

from middleware.enums import RecordTypes, DataSourceCreationResponse
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.helpers import (
    default_field_required,
)


class SourceCollectorPostRequestInnerDTO(BaseModel):
    name: str
    description: Optional[str] = None
    source_url: str
    record_type: RecordTypes
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    last_approval_editor: int
    supplying_entity: Optional[str] = None
    agency_ids: list[int]


class SourceCollectorPostRequestDTO(BaseModel):
    data_sources: list[SourceCollectorPostRequestInnerDTO]


class SourceCollectorPostResponseInnerDTO(BaseModel):
    url: str = default_field_required(description="The URL of the created data source.")
    status: DataSourceCreationResponse = default_field_required(
        description="The status of the data source creation."
    )
    data_source_id: Optional[int] = Field(
        default=None,
        description="The ID of the created data source, if successful.",
        json_schema_extra=MetadataInfo(required=True),
    )
    error: Optional[str] = Field(
        default=None,
        description="The error message, if the data source creation failed.",
        json_schema_extra=MetadataInfo(required=True),
    )


class SourceCollectorDuplicatesPostRequestDTO(BaseModel):
    urls: list[str]
