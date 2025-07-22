from typing import Optional

from pydantic import BaseModel, Field

from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


class SourceCollectorPostRequestInnerDTO(BaseModel):
    name: str = default_field_required(description="The name of the data source.")
    description: Optional[str] = default_field_not_required(
        description="The description of the data source."
    )
    source_url: str = default_field_required(description="The URL of the data source.")
    record_type: RecordTypes = default_field_required(
        description="The record type of the data source."
    )
    record_formats: list[str] = Field(
        default=[],
        description="What formats the data source can be obtained in.",
        json_schema_extra=MetadataInfo(required=False),
    )
    data_portal_type: Optional[str] = default_field_not_required(
        description="The data portal type of the data source."
    )
    last_approval_editor: int = default_field_required(
        description="User id of the user who provided approval for the data source in source collector."
    )
    supplying_entity: Optional[str] = default_field_not_required(
        description="The name of the entity that supplied the data source, if not the agency itself."
    )
    agency_ids: list[int] = default_field_required(
        description="The agencies that are associated with this data source."
    )


class SourceCollectorPostRequestDTO(BaseModel):
    data_sources: list[SourceCollectorPostRequestInnerDTO]
