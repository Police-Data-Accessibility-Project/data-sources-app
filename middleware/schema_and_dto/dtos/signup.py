from pydantic import BaseModel, Field

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class EmailOnlyDTO(BaseModel):
    email: str = Field(
        description="The user's email address",
        json_schema_extra=MetadataInfo(required=True),
    )
