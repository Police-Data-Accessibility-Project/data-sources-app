from pydantic import BaseModel

from middleware.enums import ContactFormMessageType
from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
)


class ContactFormPostDTO(BaseModel):
    email: str = default_field_required(
        description="The email of the user",
    )
    message: str = default_field_required(
        description="The message of the user",
    )
    type: ContactFormMessageType = default_field_required(
        description="The type of message",
    )
