from pydantic import BaseModel, Field

from middleware.enums import ContactFormMessageType
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class ContactFormPostDTO(BaseModel):
    email: str = Field(
        description="The email of the user",
        json_schema_extra=MetadataInfo(),
    )
    message: str = Field(
        description="The message of the user",
        json_schema_extra=MetadataInfo(),
    )
    type: ContactFormMessageType = Field(
        description="The type of message",
        json_schema_extra=MetadataInfo(),
    )
