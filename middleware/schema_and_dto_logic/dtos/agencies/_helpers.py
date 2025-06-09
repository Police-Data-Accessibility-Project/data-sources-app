from pydantic import Field

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
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
