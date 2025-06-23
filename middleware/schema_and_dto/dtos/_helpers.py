from pydantic import Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


def default_field_not_required(description: str) -> Field:
    return Field(
        default=None,
        description=description,
        json_schema_extra=MetadataInfo(required=False),
    )


def default_field_required(description: str) -> Field:
    return Field(
        description=description,
        json_schema_extra=MetadataInfo(),
    )
