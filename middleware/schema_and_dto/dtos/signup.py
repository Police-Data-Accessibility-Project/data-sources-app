from pydantic import BaseModel, Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


class EmailOnlyDTO(BaseModel):
    email: str = Field(
        description="The user's email address",
        json_schema_extra=MetadataInfo(required=True),
    )
