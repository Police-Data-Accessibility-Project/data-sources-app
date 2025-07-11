from pydantic import Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


def get_name_field(required: bool):
    return Field(
        description="The name of the agency.",
        json_schema_extra=MetadataInfo(required=required),
    )


def get_jurisdiction_type_field(required: bool):
    return Field(
        description="The highest level of jurisdiction of the agency.",
        json_schema_extra=MetadataInfo(required=required),
    )
