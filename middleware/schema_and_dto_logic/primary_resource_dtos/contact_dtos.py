from pydantic import BaseModel

from middleware.enums import ContactFormMessageType


class ContactFormPostDTO(BaseModel):
    email: str
    message: str
    type: ContactFormMessageType
