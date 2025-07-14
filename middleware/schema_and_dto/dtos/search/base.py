from typing import Optional

from pydantic import BaseModel, model_validator, Field
from werkzeug.exceptions import BadRequest

from middleware.enums import RecordTypes
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from utilities.enums import RecordCategoryEnum, SourceMappingEnum


class SearchFollowRequestBaseDTO(BaseModel):
    record_categories: Optional[list[RecordCategoryEnum]] = Field(
        default=None,
        description="Selected record categories.",
        json_schema_extra=MetadataInfo(
            required=False, source=SourceMappingEnum.QUERY_ARGS
        ),
    )
    record_types: Optional[list[RecordTypes]] = Field(
        default=None,
        description="Selected record types.",
        json_schema_extra=MetadataInfo(
            required=False, source=SourceMappingEnum.QUERY_ARGS
        ),
    )

    @model_validator(mode="before")
    def check_exclusive_fields(cls, values):
        record_categories = values.get("record_categories")
        record_types = values.get("record_types")
        if record_categories is not None and record_types is not None:
            raise BadRequest(
                "Only one of 'record_categories' or 'record_types' should be provided."
            )
        return values
